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

1.  **Clone the Repository (and switch to the backend branch):**
    ```bash
    git clone [https://github.com/pratim4dasude/echoseek.git](https://github.com/pratim4dasude/echoseek.git)
    cd echoseek
    git checkout backend
    ```

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

This service requires specific endpoints and configuration settings.

1.  **Create your secret file:** Copy the example file to create your local environment file.
    ```bash
    cp .env.example .env
    ```

2.  **Update `.env`:** Open the new `.env` file and replace the placeholder values with your actual LLM endpoint names and AWS region:
    ```ini
    LLM_ENDPOINT_NAME="YOUR_ACTUAL_LLM_ENDPOINT"
    AWS_REGION="your-aws-region"
    # ... and any other required keys
    ```

### 4. Running the Service

[Briefly explain how to run your main script or service entry point.]

*Example:*
```bash
python main_rag_service.py