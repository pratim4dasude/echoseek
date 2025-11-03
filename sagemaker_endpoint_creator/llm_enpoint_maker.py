import boto3
import sagemaker
import os
from dotenv import load_dotenv
import time
import subprocess
import sys

load_dotenv()

ROLE_ARN = os.getenv("SAGEMAKER_EXECUTION_ROLE_ARN")
# AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
NGC_API_KEY = os.getenv("NGC_API_KEY")


sm_model_name = "llama-3-1-nemotron-nano-8b-v1"
instance_type = "ml.g6e.xlarge"
public_nim_image = "public.ecr.aws/nvidia/nim:llama3.1-nemotron-nano-8b-v1-1.8.4"
payload_model = "nvidia/llama-3.1-nemotron-nano-8b-v1"

role = ROLE_ARN
nim_model = sm_model_name

sess = boto3.Session(region_name=os.getenv("us-east-1"))
region = sess.region_name

sagemaker_client = sess.client('sagemaker')
s3_client = sess.client("s3")
sts_client = sess.client('sts')
sagemaker_runtime_client = sess.client("sagemaker-runtime")

account_id = sts_client.get_caller_identity()['Account']
sagemaker_session = sagemaker.Session(boto_session=sess)

AWS_ACCOUNT_ID = account_id

print(f"AWS Region: {region} ✅")
print(f"AWS Account ID: {account_id} ✅")
print("SageMaker client ready ✅")
print("S3 client ready ✅")

print("\n--- Configuration Details ---")
print(f"Execution Role ARN: {role}")
print(f"Deployment Instance Type: {instance_type}")
print(f"SageMaker Model Name (to be deployed): {sm_model_name}")
print(f"NIM Image URI: {public_nim_image}")

print("\n--- AWS Resource Listing ---")

print("Buckets:")
buckets = s3_client.list_buckets().get("Buckets", [])
if buckets:
    for bucket in buckets:
        print(f"- {bucket['Name']}")
else:
    print("- No buckets found.")

print("\n--- SageMaker Resource Summaries ---")

response = sagemaker_client.list_notebook_instances()
print("Notebook Instances:", response.get('NotebookInstanceSummaries', []))

models = sagemaker_client.list_models()
print("Models:", models.get('ModelSummaries', []))

training_jobs = sagemaker_client.list_training_jobs().get("TrainingJobSummaries", [])
print("Training jobs:", training_jobs)

endpoints = sagemaker_client.list_endpoints().get("Endpoints", [])
print("Endpoints:", endpoints)

print("\n--- S3 Resources ---")
s3_buckets = s3_client.list_buckets().get("Buckets", [])
print("Buckets:", s3_buckets)

print("\n--- Account ID Verification (Subprocess) ---")

try:
    result = subprocess.run(
        ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    subprocess_account = result.stdout.strip()
    print(f"AWS Account ID (boto3): {account_id}")
    print(f"AWS Account ID (subprocess): {subprocess_account}")
    if subprocess_account == account_id:
        print("Account ID verification successful! ✅")
    else:
        print("WARNING: Account IDs from boto3 and subprocess do not match.")

except subprocess.CalledProcessError as e:
    print(f"Error getting AWS account ID via subprocess (Is AWS CLI installed?): {e.stderr.strip()}")


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_command(command, shell=False, check=True, input=None):

    command_display = ' '.join(command) if isinstance(command, list) and not shell else command
    print(f"\n---> Running command: {command_display}")

    try:
        # Key Change: stdout and stderr are NOT captured, allowing streaming to the console.
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            input=input,
            text=True,
            capture_output=False
        )

        return result
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Command failed with exit code {e.returncode} ", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: Required program (e.g., docker, aws) not found. Ensure it's installed and in PATH.",
              file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"!!! An unexpected error occurred: {e} !!!", file=sys.stderr)
        sys.exit(1)
def prepare_and_push_ecr_image():
    global AWS_ACCOUNT_ID

    AWS_REGION = "us-east-1"

    NIM_REPO_NAME = "llama3.1-nemotron-nano-8b-v1"
    PUBLIC_NIM_IMAGE_URI = "public.ecr.aws/nvidia/nim:llama3.1-nemotron-nano-8b-v1-1.8.4"

    if not all([AWS_REGION, AWS_ACCOUNT_ID, NIM_REPO_NAME, PUBLIC_NIM_IMAGE_URI]):
        print("Error: Missing one or more required variables in the .env file.")
        sys.exit(1)

    ECR_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
    TARGET_ECR_IMAGE = f"{ECR_URI}/{NIM_REPO_NAME}"

    print(ECR_URI)
    print(TARGET_ECR_IMAGE)

    print("          Starting ECR Image Preparation and Push ")
    print("-------------------------------------------------------------------------")
    print(f"Public Source Image: {PUBLIC_NIM_IMAGE_URI}")
    print(f"Target ECR Repository: {TARGET_ECR_IMAGE}")

    run_command(['docker', 'pull', PUBLIC_NIM_IMAGE_URI])

    print("\n---> Checking for ECR Repository...")
    result = run_command(
        ['aws', 'ecr', 'describe-repositories', '--repository-names', NIM_REPO_NAME],
        check=False
    )

    if result.returncode != 0:
        print(f"Repository '{NIM_REPO_NAME}' not found. Creating it...")
        run_command(['aws', 'ecr', 'create-repository', '--repository-name', NIM_REPO_NAME])
    else:
        print(f"Repository '{NIM_REPO_NAME}' already exists.")
    login_command = f'(aws ecr get-login-password --region {AWS_REGION}) | docker login --username AWS --password-stdin {ECR_URI}'
    run_command(login_command, shell=True)
    run_command(['docker', 'tag', PUBLIC_NIM_IMAGE_URI, TARGET_ECR_IMAGE])
    run_command(['docker', 'push', TARGET_ECR_IMAGE])

    print(f"          ECR Push Successful! Target: {TARGET_ECR_IMAGE}")
    print("------------------------------------------------------------------------------")


# prepare_and_push_ecr_image()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def deploy_sagemaker_endpoint():
    # Load necessary variables from .env
    global ROLE_ARN
    global NGC_API_KEY

    AWS_REGION = "us-east-1"
    sm_model_name = "llama-3-1-nemotron-nano-8b-v1"
    instance_type = "ml.g6e.xlarge"
    NIM_REPO_NAME = "llama3.1-nemotron-nano-8b-v1"



    if not NGC_API_KEY:
        print("FATAL ERROR: NGC_API_KEY is not set in the .env file. Deployment cannot proceed.")
        sys.exit(1)

    sess = boto3.Session(region_name=AWS_REGION)
    sm = sess.client("sagemaker")

    AWS_ACCOUNT_ID = sess.client('sts').get_caller_identity()['Account']
    nim_image = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{NIM_REPO_NAME}:latest"

    role = ROLE_ARN

    print(f"Deployment Target Model Name: {sm_model_name}")
    print(f"Deployment Target Image: {nim_image}")

    model_name = sm_model_name
    execution_role = role
    image_uri = nim_image
    api_key = NGC_API_KEY
    endpoint_config_name = model_name
    endpoint_name = model_name

    print(f"     Starting SageMaker Deployment for Model: {model_name}")
    print("----------------------------------------------------------------------------------")

    print("\n--->  Creating SageMaker Model <----------")
    container = {
        "Image": image_uri,
        "Environment": {"NGC_API_KEY": api_key}
    }

    create_model_response = sm.create_model(
        ModelName=model_name,
        ExecutionRoleArn=execution_role,
        PrimaryContainer=container
    )
    print("Model Arn: " + create_model_response["ModelArn"] + " ✅")

    print("\n--->  Creating Endpoint Configuration <----------")

    create_endpoint_config_response = sm.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                "InstanceType": instance_type,
                "InitialVariantWeight": 1,
                "InitialInstanceCount": 1,
                "ModelName": model_name,
                "VariantName": "AllTraffic",
                "ContainerStartupHealthCheckTimeoutInSeconds": 1800,
                "InferenceAmiVersion": "al2-ami-sagemaker-inference-gpu-2"

            }
        ],
    )
    print("Endpoint Config Arn: " + create_endpoint_config_response["EndpointConfigArn"] + " ✅")

    print("\n--->  Creating Endpoint (This will take a few minutes) <------------")
    create_endpoint_response = sm.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    print("Endpoint Arn: " + create_endpoint_response["EndpointArn"])

    resp = sm.describe_endpoint(EndpointName=endpoint_name)
    status = resp["EndpointStatus"]
    print(f"Current Status: {status}")

    while status in ("Creating", "Updating"):
        time.sleep(60)
        resp = sm.describe_endpoint(EndpointName=endpoint_name)
        status = resp["EndpointStatus"]
        print(f"Current Status: {status}")

    print("\n==================================================================")
    print(f"Deployment Complete!")
    print(f"Final Status: **{status}**")
    print(f"Endpoint Name: **{endpoint_name}**")
    print("==================================================================")

    if status != "InService":
        print("WARNING: Endpoint creation failed. Check SageMaker console for logs. ")


# deploy_sagemaker_endpoint(
#         model_name=sm_model_name,
#         execution_role=role,
#         image_uri=nim_image,
#         instance_type=instance_type,
#         api_key=NGC_API_KEY
#     )


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def display_endpoints():
    try:
        sm = boto3.client("sagemaker", region_name="us-east-1")
    except Exception as e:
        print(f"Error initializing Boto3 client: {e}", file=sys.stderr)
        return

    print("Endpoints:", sm.list_endpoints()["Endpoints"])
    print("EndpointConfigs:", sm.list_endpoint_configs()["EndpointConfigs"])
    print("Models:", sm.list_models()["Models"])


def deleting_endpoint():
    try:
        sm = boto3.client("sagemaker", region_name="us-east-1")
    except Exception as e:
        print(f"Error initializing Boto3 client: {e}", file=sys.stderr)
        return

    print("Endpoints:", sm.list_endpoints()["Endpoints"])
    print("EndpointConfigs:", sm.list_endpoint_configs()["EndpointConfigs"])
    print("Models:", sm.list_models()["Models"])

    sm = boto3.client("sagemaker", region_name="us-east-1")
    for ep in sm.list_endpoints()["Endpoints"]:
        name = ep["EndpointName"]
        print("Deleting endpoint:", name)
        sm.delete_endpoint(EndpointName=name)

    # 2) Endpoint Configs
    for cfg in sm.list_endpoint_configs()["EndpointConfigs"]:
        name = cfg["EndpointConfigName"]
        print("Deleting endpoint config:", name)
        sm.delete_endpoint_config(EndpointConfigName=name)

    # 3) Models
    for m in sm.list_models()["Models"]:
        name = m["ModelName"]
        print("Deleting model:", name)
        sm.delete_model(ModelName=name)

    print("✅ Cleanup requests sent.")

    print("Endpoints:", sm.list_endpoints()["Endpoints"])
    print("EndpointConfigs:", sm.list_endpoint_configs()["EndpointConfigs"])
    print("Models:", sm.list_models()["Models"])


def llm_endpoin_creator():

    import time
    start_time = time.time()

    display_endpoints()
    prepare_and_push_ecr_image()
    deploy_sagemaker_endpoint()
    display_endpoints()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Function  execution time: **{execution_time:.6f} seconds**")

    # deleting_endpoint()

if __name__ == '__main__':
    llm_endpoin_creator()
