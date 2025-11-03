import json
from typing import Dict, Any, Optional

from langchain_aws.llms.sagemaker_endpoint import LLMContentHandler
from langchain_aws.llms import SagemakerEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

PAYLOAD_MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
LLM_ENDPOINT_NAME = "llama-3-1-nemotron-nano-8b-v1"
AWS_REGION = "us-east-1"


class CustomChatContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict[str, Any]) -> bytes:

        max_tokens = model_kwargs.pop("max_tokens", 3000)

        payload = {
            "model": PAYLOAD_MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "detailed thinking off"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens
        }

        input_str = json.dumps(payload)
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:

        response_json = json.loads(output.read().decode("utf8"))

        try:

            generated_text = response_json["choices"][0]["message"]["content"]
            return generated_text.strip()
        except (KeyError, IndexError) as e:

            if isinstance(response_json, dict) and "generated_text" in response_json:
                return response_json["generated_text"].strip()

            print(f"ERROR: Failed to parse model output structure.")
            raise ValueError(
                f"Could not extract generated text. Raw response starts with: {str(response_json)[:100]}...")


def get_llm_chain() -> Runnable:
    llm_handler = CustomChatContentHandler()

    llm_model_kwargs = {
        "max_tokens": 3000,
    }

    sagemaker_llm = SagemakerEndpoint(
        endpoint_name=LLM_ENDPOINT_NAME,
        region_name=AWS_REGION,
        model_kwargs=llm_model_kwargs,
        content_handler=llm_handler,
    )

    prompt = PromptTemplate.from_template("{query}")

    chain = (
            prompt
            | sagemaker_llm
            | StrOutputParser()
    )

    return chain


def llm_chat(chat: str):

    inference_chain = get_llm_chain()

    user_question = chat

    print(f"--->  Calling SageMaker Endpoint: {LLM_ENDPOINT_NAME} ---")
    print(f"Query: {user_question}\n")
    print("... Awaiting for SageMaker inference ...\n")

    final_answer = ""

    try:
        final_answer = inference_chain.invoke({"query": user_question})

        print("--->   Final Answer from LLM LangChain ---")
        print(final_answer)
        return final_answer

    except Exception as e:
        print("\n--- ERROR DURING INFERENCE ---")
        print("Please ensure your endpoint is running, the name is correct, and your AWS credentials are configured.")
        print(f"Details: {e}")

    return "Error Occur -- no output decided"


if __name__ == '__main__':
    r = llm_chat("what are you doing today? ")
    print(r)
