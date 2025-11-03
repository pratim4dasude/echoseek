import json
from typing import Dict, Any, List, Union
from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain_core.documents import Document


class CustomEmbeddingsContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, texts: List[str], model_kwargs: Dict[str, Any]) -> bytes:
        PAYLOAD_MODEL_NAME = "nvidia/llama-3.2-nv-embedqa-1b-v2"
        INPUT_TYPE = "query"
        payload = {
            "input": texts,
            "model": PAYLOAD_MODEL_NAME,
            "input_type": INPUT_TYPE
        }

        input_str = json.dumps(payload)
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf8"))

        try:
            if isinstance(response_json, dict) and "data" in response_json:
                data_list = response_json["data"]
                if isinstance(data_list, list) and all(isinstance(d, dict) and "embedding" in d for d in data_list):
                    return [d["embedding"] for d in data_list]

            if "embedding" in response_json:
                return response_json["embedding"]
            elif "vector" in response_json:
                return response_json["vector"]
            elif isinstance(response_json, list) and all(isinstance(v, list) for v in response_json):
                return response_json
            elif isinstance(response_json, list) and all(
                    isinstance(d, dict) and "embedding" in d for d in response_json):
                return [d["embedding"] for d in response_json]

            raise KeyError("Could not find embedding vectors in the model response.")

        except Exception as e:
            print(f"ERROR: Failed to parse embedding output structure: {e}")
            print(f"Raw model output received (first 100 chars): {str(response_json)[:100]}...")
            raise ValueError("Could not extract embedding vectors from model response.")


def embedding_chat(chat: List[str]):
    EMBEDDING_ENDPOINT_NAME = "nim-llama-3-2-nv-embedqa-1b-v2"
    AWS_REGION = "us-east-1"
    # PAYLOAD_MODEL_NAME = "nvidia/llama-3.2-nv-embedqa-1b-v2"
    # INPUT_TYPE = "query"

    embeddings_handler = CustomEmbeddingsContentHandler()

    model_kwargs = {}

    sagemaker_embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=EMBEDDING_ENDPOINT_NAME,
        region_name=AWS_REGION,
        model_kwargs=model_kwargs,
        content_handler=embeddings_handler,
    )

    # texts_to_embed = [
    #     "What is the capital of France?",
    #     "The Eiffel Tower is in Paris.",
    #     "A deep dive into transformer architecture.",
    # ]

    texts_to_embed = chat

    print(f"--- Calling SageMaker Embedding Endpoint: {EMBEDDING_ENDPOINT_NAME} ---")
    print(f"Texts to embed: {len(texts_to_embed)}\n")
    print("... Awaiting response from SageMaker inference ...\n")

    try:
        vectors = sagemaker_embeddings.embed_documents(texts_to_embed)

        # output_filename = "embeddings_output.json"
        # with open(output_filename, 'w') as f:
        #     json.dump(vectors, f, indent=2)

        print("--- Embeddings Success ---")
        print(f"Total Vectors Received: {len(vectors)}")

        if vectors:
            vector_dim = len(vectors[0])
            print(f"Vector Dimension: {vector_dim}")

            print("\nFirst Vector (Truncated):")
            print(vectors[0][:5], "...")

            return vectors

    except Exception as e:
        print("\n--- ERROR DURING EMBEDDING INFERENCE ---")
        print("Please ensure your endpoint is running, the name is correct, and your AWS credentials are configured.")
        print(f"Details: {e}")


if __name__ == '__main__':
    texts_to_embed = [
        "What is the capital of France?",
        "The Eiffel Tower is in Paris.",
        "A deep dive into transformer architecture.",
    ]

    embeddings = embedding_chat(texts_to_embed)

    print(embeddings)
