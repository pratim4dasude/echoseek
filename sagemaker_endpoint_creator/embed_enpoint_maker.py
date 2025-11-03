import boto3
import json
import sagemaker
import os
import io
import time
from dotenv import load_dotenv
import subprocess
import sys

load_dotenv()

ROLE_ARN = os.getenv("SAGEMAKER_EXECUTION_ROLE_ARN")
NGC_API_KEY = os.getenv("NGC_API_KEY")
# AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")


PUBLIC_NIM_IMAGE = "public.ecr.aws/nvidia/nim:llama3.2-nv-embedqa-1b-v2-1.3.0"
NIM_MODEL = "nim-llama-3-2-nv-embedqa-1b-v2"
SM_MODEL_NAME = "nim-llama-3-2-nv-embedqa-1b-v2"
INSTANCE_TYPE = "ml.g5.xlarge"
PAYLOAD_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"
AWS_REGION = "us-east-1"

sess = boto3.Session()
sagemaker_session = sagemaker.Session(boto_session=sess)

sm_client = sess.client("sagemaker")
s3_client = sess.client("s3")
sts_client = sess.client('sts')
sagemaker_runtime_client = sess.client("sagemaker-runtime")

region = sess.region_name
role = ROLE_ARN
account_id = sts_client.get_caller_identity()['Account']

AWS_ACCOUNT_ID = account_id

print("--- AWS and SageMaker Context ---")
print(f"SageMaker client ready ✅")
print(f"Current AWS Region: {region}")
print(f"AWS Account ID -----> : {account_id}")
print(f"Execution Role ARN: {role}")
print(f"Model Image (from .env): {PUBLIC_NIM_IMAGE}")
print(f"Instance Type (from .env): {INSTANCE_TYPE}")

print("\n--- SageMaker Resources ---")
response = sm_client.list_notebook_instances()
print("Notebook Instances:", response.get('NotebookInstanceSummaries', []))
models = sm_client.list_models()
print("Models:", models.get('ModelSummaries', []))
training_jobs = sm_client.list_training_jobs().get("TrainingJobSummaries", [])
print("Training jobs:", training_jobs)

endpoints = sm_client.list_endpoints().get("Endpoints", [])
print("Endpoints:", endpoints)

print("\n--- S3 Resources ---")
s3_buckets = s3_client.list_buckets().get("Buckets", [])
print("Buckets:", s3_buckets)

print("\n--- subprocess  ---")
result = subprocess.run(
    ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print(f"Error getting AWS acc ID : {result.stderr}")
else:
    account_cli = result.stdout.strip()
    print(f"AWS account ID  : {account_cli}")


def run_command(command, shell=False, check=True, input=None):
    command_display = ' '.join(command) if isinstance(command, list) and not shell else command
    print(f"\n---> Running command: {command_display}")

    try:
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
        print(f"\n Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Required program (e.g., docker, aws) not found. Ensure it's installed and in PATH.",
              file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def prepare_and_push_ecr_image():


    try:
        sess = boto3.Session(region_name=AWS_REGION)
        sts_client = sess.client('sts')
        AWS_ACCOUNT_ID = sts_client.get_caller_identity()['Account']
    except Exception as e:
        print(f"Error initializing AWS session or getting account ID: {e}", file=sys.stderr)
        sys.exit(1)

    NIM_REPO_NAME = SM_MODEL_NAME
    PUBLIC_NIM_IMAGE_URI = PUBLIC_NIM_IMAGE

    if not all([AWS_REGION, AWS_ACCOUNT_ID, NIM_REPO_NAME, PUBLIC_NIM_IMAGE_URI]):
        print(
            "Error: Missing one or more required variables (AWS_REGION, AWS_ACCOUNT_ID, NIM_REPO_NAME, or PUBLIC_NIM_IMAGE_URI).",
            file=sys.stderr)
        sys.exit(1)

    ECR_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
    TARGET_ECR_IMAGE = f"{ECR_URI}/{NIM_REPO_NAME}"

    print(f"AWS Region: {AWS_REGION}")
    print(f"AWS Account ID: {AWS_ACCOUNT_ID}")
    print(f"Base ECR URI: {ECR_URI}")
    print(f"Target Image URI: {TARGET_ECR_IMAGE}")

    print("     Starting ECR Image Preparation and Push docker ")
    print("--------------------------------------------------------------------------")
    print(f"Public Source Image: {PUBLIC_NIM_IMAGE_URI}")
    print(f"Target ECR Repository: {TARGET_ECR_IMAGE}")

    # 1. Pull the source image
    run_command(['docker', 'pull', PUBLIC_NIM_IMAGE_URI])

    # 2. Check for ECR Repository and Create if necessary
    print("\n---> Checking for ECR Repository...")
    # Using check=False here to allow the command to fail gracefully if the repo doesn't exist
    result = run_command(
        ['aws', 'ecr', 'describe-repositories', '--repository-names', NIM_REPO_NAME],
        check=False
    )

    if result.returncode != 0:
        print(f"Repository '{NIM_REPO_NAME}' not found. Creating it...")
        run_command(['aws', 'ecr', 'create-repository', '--repository-name', NIM_REPO_NAME])
    else:
        print(f"Repository '{NIM_REPO_NAME}' already exists.")

    # 3. Docker Login using AWS CLI password pipe (requires shell=True)
    print("\n---> Logging into ECR...")
    # The pipe must be executed via shell=True
    login_command = f'(aws ecr get-login-password --region {AWS_REGION}) | docker login --username AWS --password-stdin {ECR_URI}'
    # Note: Setting capture_output=False here helps see progress/prompts during shell execution
    run_command(login_command, shell=True)

    # 4. Tag the image
    print("\n---> Tagging image...")
    run_command(['docker', 'tag', PUBLIC_NIM_IMAGE_URI, TARGET_ECR_IMAGE])

    # 5. Push the image
    print("\n---> Pushing image to ECR...")
    # Note: Setting capture_output=False here helps see push progress
    run_command(['docker', 'push', TARGET_ECR_IMAGE])

    print(f"          ECR Push Successful! Target: {TARGET_ECR_IMAGE}")
    print("\n--------------------------------------------------------------------")


# prepare_and_push_ecr_image()

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def deploy_sagemaker_endpoint():
    global ROLE_ARN
    global NGC_API_KEY

    SM_MODEL_NAME = "nim-llama-3-2-nv-embedqa-1b-v2"
    INSTANCE_TYPE = "ml.g5.xlarge"

    try:
        sess = boto3.Session()
        sm_client = sess.client("sagemaker")
        sts_client = sess.client('sts')

        AWS_REGION = sess.region_name
        AWS_ACCOUNT_ID = sts_client.get_caller_identity()['Account']

    except Exception as e:
        print(f"Error initializing AWS session: {e}", file=sys.stderr)
        sys.exit(1)

    NIM_IMAGE_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{SM_MODEL_NAME}:latest"

    print(NIM_IMAGE_URI)

    model_name = SM_MODEL_NAME
    execution_role = ROLE_ARN
    image_uri = NIM_IMAGE_URI
    instance_type = INSTANCE_TYPE
    api_key = NGC_API_KEY

    print("           Starting SageMaker Endpoint Deployment             ")
    print("\n ----------------------------------------------------------------------")

    if not all([execution_role, model_name, instance_type, api_key]):
        print("!!! ERROR: Missing required function arguments. Cannot deploy. !!!", file=sys.stderr)
        sys.exit(1)

    print(f"Deployment Target: {model_name}")
    print(f"Instance Type: {instance_type}")

    endpoint_config_name = model_name
    endpoint_name = model_name

    print("\n--->  Creating SageMaker Model <-----------------")
    container = {
        "Image": image_uri,
        "Environment": {"NGC_API_KEY": api_key}
    }

    try:
        create_model_response = sm_client.create_model(
            ModelName=model_name,
            ExecutionRoleArn=execution_role,
            PrimaryContainer=container
        )
        print("Model Arn: " + create_model_response["ModelArn"] + " ✅")
    except sm_client.exceptions.ResourceInUse:
        print(f"Model {model_name} already exists. Skipping model creation.")
    except Exception as e:
        print(f"Error creating model: {e}", file=sys.stderr)
        return

    # 3. Create Endpoint Configuration
    print("\n--->  Creating Endpoint Configuration <------------------")

    try:
        create_endpoint_config_response = sm_client.create_endpoint_config(
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
    except sm_client.exceptions.ResourceInUse:
        print(f"Endpoint Config {endpoint_config_name} already exists. Skipping config creation.")
    except Exception as e:
        print(f"Error creating endpoint config: {e}", file=sys.stderr)
        return

    print("\n--->  Creating Endpoint <-------------")

    try:
        create_endpoint_response = sm_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        print("Endpoint Arn: " + create_endpoint_response["EndpointArn"])
    except sm_client.exceptions.ResourceInUse:
        print(f"Endpoint {endpoint_name} already exists. Proceeding to check status.")
    except Exception as e:
        print(f"Error creating endpoint: {e}", file=sys.stderr)
        return

    print("\n---  Endpoint Creation  ---")

    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    status = resp["EndpointStatus"]
    print(f"Current Status: {status}")

    while status in ("Creating", "Updating"):
        time.sleep(60)  # Wait 60 seconds
        resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
        status = resp["EndpointStatus"]
        print(f"Current Status: {status}")

    print("\n--------------------------------------------------------------------")
    print("Deployment Complete!")
    print(f"Final Status: **{status}**")
    print(f"Endpoint Name: **{endpoint_name}**")
    print("--------------------------------------------------------------------------")

    if status != "InService":
        print("WARNING: Endpoint creation failed. Check SageMaker console for logs.")


# deploy_sagemaker_endpoint()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


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

    for cfg in sm.list_endpoint_configs()["EndpointConfigs"]:
        name = cfg["EndpointConfigName"]
        print("Deleting endpoint config:", name)
        sm.delete_endpoint_config(EndpointConfigName=name)

    for m in sm.list_models()["Models"]:
        name = m["ModelName"]
        print("Deleting model:", name)
        sm.delete_model(ModelName=name)

    print(" Cleanup requests sent.")

    print("Endpoints:", sm.list_endpoints()["Endpoints"])
    print("EndpointConfigs:", sm.list_endpoint_configs()["EndpointConfigs"])
    print("Models:", sm.list_models()["Models"])


def embed_endpoint_creator():
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
    # display_endpoints()


if __name__ == '__main__':
    embed_endpoint_creator()
