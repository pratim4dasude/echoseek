# 🐍 RAG Stylist Backend Service

This repository section contains the **Python-based Retrieval-Augmented Generation (RAG) backend service** for the e-commerce application. This service handles product search, context retrieval, and generates personalized, chat-history-aware styling recommendations using a Large Language Model (LLM) and product data.

This code is hosted on the dedicated **`backend`** branch.

---

## 🛠️ Tech Stack & Architecture

* **Language:** Python
* **Frameworks:** LangChain, Pydantic (or similar data/chaining libraries)
* **Vector Store:** [FAISS, Chroma, etc. - Specify which you used]
* **LLM Integration:** AWS SageMaker Endpoints (or [Specify your LLM API, e.g., OpenAI, Gemini])
* **Data:** Product Vector Embeddings

---

## 🚀 Getting Started

Follow these steps to set up and run the service locally.

### 1. Requirements

* Python 3.9+
* Access to the required AWS SageMaker LLM and Embedding endpoints.
* Your API keys/credentials configured (typically via your local AWS CLI configuration).

### 2. Setup
### 2. Setup

1.  **Clone the Backend Branch Only:**
    Use the `--single-branch` option to clone *only* the contents of the dedicated `backend` branch.
    ```bash
    git clone --single-branch --branch backend https://github.com/pratim4dasude/echoseek.git
    cd echoseek
    ```
    > **Note:** If you already cloned the full repository, you can simply use `cd echoseek` and then `git checkout backend`.

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file listing all your project's Python libraries.)*

### 3. Environment Variables

This service requires specific security credentials and API keys.

1.  **Create your secret file:** Copy the example file to create your local environment file.
    ```bash
    cp .env.example .env
    ```

2.  **Update `.env`:** Open the new `.env` file and replace the placeholder values with your credentials:

    ```ini
    # AWS/SageMaker Execution Role ARN
    SAGEMAKER_EXECUTION_ROLE_ARN=""

    # NVIDIA GPU Cloud (NGC) API Key 
    NGC_API_KEY="" 
    
    # OpenAI API Key 
    OPENAI_API_KEY=""
    ```

---
### 4. Deploying the SageMaker Endpoints

Before running the main RAG service, you **must** deploy the required LLM and Embedding models to AWS SageMaker Endpoints using the included helper files.

#### ⚠️ IAM Role Requirement

Ensure that the IAM role associated with your AWS environment (the role launching the SageMaker tasks) has the necessary permissions. You **must** have the following policy attached:

* **`AmazonEC2ContainerRegistryFullAccess`**

This policy is required to create the two private ECR repositories that will host the Docker images for the models.

#### 1. Start Docker Desktop

Ensure **Docker Desktop is running** on your local machine, as the deployment script requires it to build and push the necessary container images.

#### 2. Run Endpoint Creation Scripts

Navigate to the `sagemaker_endpoint_creator` directory and execute the endpoint creation functions for both the LLM and the Embedding model.

The files contain functions like `embed_endpoint_creator()` and `llm_endpoint_creator()` that handle:
* `display_endpoints()`
* `prepare_and_push_ecr_image()` (Requires Docker)
* `deploy_sagemaker_endpoint()`

Run both scripts sequentially (the exact execution command will depend on how these files are structured, but this is the general idea):

```bash
# Example command - adjust based on your file structure
# Execute the script to create the Embedding Endpoint
python sagemaker_endpoint_creator/embed_endpoint_file.py 

# Execute the script to create the LLM Endpoint
python sagemaker_endpoint_creator/llm_endpoint_file.py
```

### 5. Endpoint Validation

After the endpoints show an **'InService'** status on AWS, run the standalone test files to confirm local connectivity via LangChain.

```bash
# Test the Generative LLM Endpoint connection
python llm_standaloe_langcahin.py

# Test the Embedding Model Endpoint connection
python embed_standalone_langchain.py
```

### 6. Running the RAG Service

Once the SageMaker Endpoints are active and validated, you can start the local Python RAG server which will handle API calls from the frontend application.

```bash
python backend.py
```

