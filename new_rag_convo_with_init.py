# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                  SECOND QUERY - REWRITE  ( RAG )
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# import json
# from typing import Dict, Any, List, Union, Tuple, Optional
#
# from langchain_core.documents import Document
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnableParallel, RunnablePassthrough, Runnable
#
# from langchain_aws.llms.sagemaker_endpoint import LLMContentHandler
# from langchain_aws.llms import SagemakerEndpoint
# from langchain_community.embeddings import SagemakerEndpointEmbeddings
# from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
# from langchain_community.vectorstores import FAISS
#
# LLM_ENDPOINT_NAME = "llama-3-1-nemotron-nano-8b-v1"
# LLM_PAYLOAD_MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
# AWS_REGION = "us-east-1"
#
# EMBEDDING_ENDPOINT_NAME = "nim-llama-3-2-nv-embedqa-1b-v2"
# EMBEDDING_PAYLOAD_MODEL_NAME = "nvidia/llama-3.2-nv-embedqa-1b-v2"
# EMBEDDING_INPUT_TYPE = "query"
#
# DEFAULT_CATALOG_PATH = r"C:\Users\KIIT\PycharmProjects\sagemaker_workings\products_with_caps.json"
# TOP_K = 3
#
# class CustomChatContentHandler(LLMContentHandler):
#     content_type = "application/json"
#     accepts = "application/json"
#
#     def transform_input(self, prompt: str, model_kwargs: Dict[str, Any]) -> bytes:
#         max_tokens = model_kwargs.pop("max_tokens", 3000)
#         payload = {
#             "model": LLM_PAYLOAD_MODEL_NAME,
#             "messages": [
#                 {"role": "system", "content": "detailed thinking off"},
#                 {"role": "user", "content": prompt},
#             ],
#             "max_tokens": max_tokens,
#         }
#         return json.dumps(payload).encode("utf-8")
#
#     def transform_output(self, output: bytes) -> str:
#         response_json = json.loads(output.read().decode("utf8"))
#         try:
#             return response_json["choices"][0]["message"]["content"].strip()
#         except (KeyError, IndexError):
#             if isinstance(response_json, dict) and "generated_text" in response_json:
#                 return response_json["generated_text"].strip()
#             raise ValueError(
#                 f"Could not extract generated text. Raw response starts with: {str(response_json)[:200]}..."
#             )
#
#
# class CustomEmbeddingsContentHandler(EmbeddingsContentHandler):
#     content_type = "application/json"
#     accepts = "application/json"
#
#     def transform_input(self, texts: List[str], model_kwargs: Dict[str, Any]) -> bytes:
#         payload = {
#             "input": texts,
#             "model": EMBEDDING_PAYLOAD_MODEL_NAME,
#             "input_type": EMBEDDING_INPUT_TYPE,
#         }
#         return json.dumps(payload).encode("utf-8")
#
#     def transform_output(self, output: bytes) -> List[List[float]]:
#         response_json = json.loads(output.read().decode("utf8"))
#         if isinstance(response_json, dict) and "data" in response_json:
#             data_list = response_json["data"]
#             if isinstance(data_list, list):
#                 embs = []
#                 for d in data_list:
#                     if isinstance(d, dict) and "embedding" in d:
#                         embs.append(d["embedding"])
#                 if embs:
#                     return embs
#         raise ValueError("Could not extract embedding vectors from model response.")
#
#
# def load_catalog_from_file(filepath: str) -> List[Dict[str, Any]]:
#     try:
#         with open(filepath, "r", encoding="utf-8") as f:
#             print(f"Loading product catalog from {filepath}...")
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"[WARN] Catalog not found: {filepath}. Using empty list.")
#         return []
#     except json.JSONDecodeError as e:
#         print(f"[WARN] JSON decode error for {filepath}: {e}. Using empty list.")
#         return []
#
#
# def _pick(d: Dict[str, Any], *keys: str, default=None):
#     for k in keys:
#         if k in d and d[k] not in (None, "", [], {}):
#             return d[k]
#     return default
#
#
# def normalize_for_frontend(prod: Dict[str, Any]) -> Dict[str, Any]:
#
#     return {
#         "id": str(_pick(prod, "id", "product_id", "asin", default="")),
#         "title": _pick(prod, "title", "name", "product_title", default="Untitled Product"),
#         "url": _pick(prod, "url", "link", "href", "product_url", default=""),
#         "image": _pick(prod, "image", "image_url", "thumbnail", "thumb", "img", default=None),
#         "price": str(_pick(prod, "price", "price_text", "amount", default="")),
#         "rating": _pick(prod, "rating", "stars", default=None),
#         "color": _pick(prod, "color", "colour", default=None),
#         "size": _pick(prod, "size", default=None),
#         "category": _pick(prod, "category", "cat", default=None),
#         "product_details": _pick(prod, "product_details", "Product_Details", "details", "description", "caption", default=""),
#     }
#
# def _doc_text_from_product(prod: Dict[str, Any]) -> str:
#
#     p = normalize_for_frontend(prod)
#     fields = [
#         ("title", p.get("title", "")),
#         ("product_details", p.get("product_details", "")),
#         ("category", p.get("category", "")),
#         ("color", p.get("color", "")),
#         ("size", p.get("size", "")),
#         ("price", "" if p.get("price") in (None, "", []) else str(p["price"])),
#         ("rating", "" if p.get("rating") in (None, "", []) else str(p["rating"])),
#     ]
#
#     return "\n".join(f"{k}: {v}".strip() for k, v in fields if str(v).strip() != "")
#
#
# def build_documents(catalog: List[Dict[str, Any]]) -> List[Document]:
#     docs: List[Document] = []
#     print("\n--- INDEXING LOG: EMBEDDING INPUT TEXTS ---")
#     for i, prod in enumerate(catalog, start=1):
#         text = _doc_text_from_product(prod)
#         pid = str(prod.get("id", ""))  # still okay to log/debug by ID
#         preview = text.replace("\n", " | ")
#         print(f"[{i}] [ID {pid}] EMBEDDING INPUT: {preview[:140]}...")
#         docs.append(Document(page_content=text, metadata=prod))
#     print("--- END INDEXING LOG ---\n")
#
#     try:
#         docs_dump = [{"page_content": d.page_content, "metadata": d.metadata} for d in docs]
#         with open("documents.json", "w", encoding="utf-8") as f:
#             json.dump(docs_dump, f, ensure_ascii=False, indent=2)
#         print("✅ Saved documents.json")
#     except Exception as e:
#         print(f"[WARN] Could not write documents.json: {e}")
#
#     if not docs:
#         raise ValueError("No valid products to index.")
#     return docs
#
#
#
# def format_docs_for_llm(docs: List[Document]) -> str:
#     return "\n---\n".join(doc.page_content for doc in docs)
#
#
# def extract_full_products(docs: List[Document]) -> List[Dict[str, Any]]:
#     return [doc.metadata for doc in docs]
#
#
#
# EXPLANATION_PROMPT = """You are an expert e-commerce product recommender.
#
# Based ONLY on the product details described in the CONTEXT, write a single, brief paragraph (3-4 sentences maximum) explaining to the user why the retrieved products are the best match for their QUESTION. Highlight how the products match the user's criteria (e.g., color, fit, price).
#
# CONTEXT:
# {context}
#
# QUESTION:
# {question}
#
# EXPLANATION:"""
#
# QUESTION_REWRITE_PROMPT = """You are a helpful assistant that rewrites follow-up shopping questions into a standalone query.
#
# Rewrite the FOLLOW_UP so it can be understood without chat history, but still reflects the user's context and constraints.
#
# CHAT HISTORY (most recent last):
# {history}
#
# FOLLOW_UP:
# {question}
#
# STANDALONE_QUERY:"""
#
#
#
# def get_rag_chain(catalog: List[Dict[str, Any]]) -> Tuple[Runnable, FAISS]:
#     if not catalog:
#         print("Error: Catalog is empty. Cannot initialize RAG chain.")
#         return None, None
#
#     print("--- Initializing Embeddings and LLM ---")
#     documents = build_documents(catalog)
#
#     # Embeddings
#     embeddings_handler = CustomEmbeddingsContentHandler()
#     sagemaker_embeddings = SagemakerEndpointEmbeddings(
#         endpoint_name=EMBEDDING_ENDPOINT_NAME,
#         region_name=AWS_REGION,
#         model_kwargs={},
#         content_handler=embeddings_handler,
#     )
#
#     print(f"Indexing {len(documents)} products into FAISS...")
#     vectorstore = FAISS.from_documents(documents, sagemaker_embeddings)
#     retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
#
#     # LLM
#     llm_handler = CustomChatContentHandler()
#     sagemaker_llm = SagemakerEndpoint(
#         endpoint_name=LLM_ENDPOINT_NAME,
#         region_name=AWS_REGION,
#         model_kwargs={"max_tokens": 512},
#         content_handler=llm_handler,
#     )
#
#     llm_explanation_chain = (
#         PromptTemplate.from_template(EXPLANATION_PROMPT)
#         | sagemaker_llm
#         | StrOutputParser()
#     )
#
#     rag_chain = (
#         retriever
#         | RunnableParallel({
#             "llm_recommendation": (
#                 RunnableParallel(
#                     {"context": format_docs_for_llm, "question": RunnablePassthrough()}
#                 )
#                 | llm_explanation_chain
#             ),
#             "products_json": extract_full_products,
#         })
#     )
#
#     print("Product Selector RAG Chain fully constructed.")
#     return rag_chain, vectorstore
#
#
# try:
#     from build_product_data import build_products_from_query
# except Exception:
#     def build_products_from_query(seed_query: str):
#         print(f"[WARN] Using fallback build_products_from_query with seed: {seed_query!r}")
#         path = DEFAULT_CATALOG_PATH
#         return path, load_catalog_from_file(path)
#
#
# def build_ranked_products(vectorstore: FAISS, query: str, k: int = TOP_K) -> List[Dict[str, Any]]:
#
#     results = vectorstore.similarity_search_with_score(query, k=k)
#     results = sorted(results, key=lambda x: x[1])  # by score asc
#     ranked: List[Dict[str, Any]] = []
#     seen = set()
#     for doc, _score in results:
#         meta = doc.metadata or {}
#         pid = str(meta.get("id", ""))
#         if pid in seen:
#             continue
#         ranked.append(normalize_for_frontend(meta))
#         seen.add(pid)
#     return ranked
#
#
# def make_question_rewriter(llm: SagemakerEndpoint) -> Runnable:
#     return PromptTemplate.from_template(QUESTION_REWRITE_PROMPT) | llm | StrOutputParser()
#
#
# class ChatRAG:
#     def __init__(self):
#         self.chat_history: List[Tuple[str, str]] = []
#         self.rag_chain: Optional[Runnable] = None
#         self.vectorstore: Optional[FAISS] = None
#         self.catalog_path: Optional[str] = None
#         self.products_cache: List[Dict[str, Any]] = []
#
#         self._llm = SagemakerEndpoint(
#             endpoint_name=LLM_ENDPOINT_NAME,
#             region_name=AWS_REGION,
#             model_kwargs={"max_tokens": 256},
#             content_handler=CustomChatContentHandler(),
#         )
#         self._rewriter = make_question_rewriter(self._llm)
#
#     def _reindex_from_products(self, products: List[Dict[str, Any]]):
#         self.rag_chain, self.vectorstore = get_rag_chain(products)
#         self.products_cache = products
#
#     def _ensure_initialized(self, first_query: Optional[str] = None):
#         if self.rag_chain is None or self.vectorstore is None:
#             # Prefer dynamic build via first user query; else fallback to default file.
#             seed = (first_query or "").strip()
#             path, products = build_products_from_query(seed)
#             if not products:
#                 products = load_catalog_from_file(path) if path else []
#             if not products:
#                 # final fallback to default constant
#                 products = load_catalog_from_file(DEFAULT_CATALOG_PATH)
#             if not products:
#                 raise RuntimeError("Product catalog could not be built/loaded for first turn.")
#             self.catalog_path = path
#             self._reindex_from_products(products)
#
#     def reset(self):
#         self.chat_history.clear()
#         self.rag_chain = None
#         self.vectorstore = None
#         self.catalog_path = None
#         self.products_cache = []
#
#     @staticmethod
#     def _history_to_text(history: List[Tuple[str, str]], max_turns: int = 6) -> str:
#         tail = history[-max_turns:]
#         if not tail:
#             return "(no history)"
#         lines = []
#         for u, a in tail:
#             lines.append(f"User: {u}")
#             lines.append(f"Assistant: {a}")
#         return "\n".join(lines)
#
#     def ask(self, user_message: str, k: int = TOP_K) -> Dict[str, Any]:
#         initializing = (self.rag_chain is None or self.vectorstore is None)
#         self._ensure_initialized(first_query=user_message if initializing else None)
#
#         if not self.rag_chain or not self.vectorstore:
#             raise RuntimeError("RAG components not initialized.")
#
#         used_history = len(self.chat_history) > 0
#         if used_history:
#             history_text = self._history_to_text(self.chat_history)
#             rewritten = (self._rewriter.invoke({"history": history_text, "question": user_message}) or "").strip()
#             standalone_query = rewritten or user_message
#         else:
#             standalone_query = user_message
#
#         result = self.rag_chain.invoke(standalone_query)
#         human_text = (result.get("llm_recommendation") or "").strip()
#
#         ranked_products = build_ranked_products(self.vectorstore, standalone_query, k=k)
#
#         self.chat_history.append((user_message, human_text if human_text else "(no answer)"))
#
#         pretty = (
#             "HUMAN RECOMMENDATION (LLM TEXT):\n"
#             f"{human_text}\n\n"
#             "PROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):\n"
#             f"{json.dumps(ranked_products, ensure_ascii=False, indent=2)}"
#         )
#
#         return {
#             "human_recommendation": human_text,
#             "products": ranked_products,
#             "pretty_print": pretty,
#             "meta": {
#                 "rewritten_query": standalone_query,
#                 "used_history": used_history and (standalone_query != user_message),
#                 "initialized_this_turn": initializing,
#             },
#         }
#
#
# chat_rag = ChatRAG()
#
#
#
# if __name__ == "__main__":
#     import json
#
#     chat_rag.reset()
#
#     turn_1 = "i want stylish shirt for mens age 20 size xl for winter wera"
#     turn_2 = "and make it formal, budget under 1500"
#     turn_3 = "beige color would be great"
#
#     print("\n" + "=" * 80)
#     print("[TURN 1]")
#     print(f"USER QUERY: {turn_1}\n")
#
#     r1 = chat_rag.ask(turn_1)
#     print("HUMAN RECOMMENDATION (LLM TEXT):")
#     print(r1["human_recommendation"])
#     print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
#     print(json.dumps(r1["products"], ensure_ascii=False, indent=2))
#
#
#     print("\n" + "=" * 80)
#     print("[TURN 2]")
#     print(f"USER QUERY: {turn_2}\n")
#
#     r2 = chat_rag.ask(turn_2)
#     print("HUMAN RECOMMENDATION (LLM TEXT):")
#     print(r2["human_recommendation"])
#     print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
#     print(json.dumps(r2["products"], ensure_ascii=False, indent=2))
#
#     print("\n" + "=" * 80)
#     print("[TURN 3]")
#     print(f"USER QUERY: {turn_3}\n")
#
#     r3 = chat_rag.ask(turn_3)
#     print("HUMAN RECOMMENDATION (LLM TEXT):")
#     print(r3["human_recommendation"])
#     print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
#     print(json.dumps(r3["products"], ensure_ascii=False, indent=2))
#
#     print("\n" + "=" * 80)
#     print("✅ Conversation complete.\n")

# ///////////////////////////////////////////////////////////////
#         ^^      SECOND QUERY REWRITE (RAG )  ^^
# //////////////////////////////////////////////////////////////


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                                  SECOND QUERY hold HISTORY of FIRST QUERY

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import json
import re
from typing import Dict, Any, List, Tuple, Optional
from operator import itemgetter

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, Runnable
from langchain_aws.llms.sagemaker_endpoint import LLMContentHandler
from langchain_aws.llms import SagemakerEndpoint
from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain_community.vectorstores import FAISS

LLM_ENDPOINT_NAME = "llama-3-1-nemotron-nano-8b-v1"
LLM_PAYLOAD_MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
AWS_REGION = "us-east-1"

EMBEDDING_ENDPOINT_NAME = "nim-llama-3-2-nv-embedqa-1b-v2"
EMBEDDING_PAYLOAD_MODEL_NAME = "nvidia/llama-3.2-nv-embedqa-1b-v2"
EMBEDDING_INPUT_TYPE = "query"

DEFAULT_CATALOG_PATH = r"products.json"
TOP_K = 4


class CustomChatContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict[str, Any]) -> bytes:
        max_tokens = model_kwargs.pop("max_tokens", 3000)
        temperature = model_kwargs.pop("temperature", 0.7)
        payload = {
            "model": LLM_PAYLOAD_MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, modern fashion stylist. "
                        "Give natural outfit advice without sounding robotic. "
                        "Be warm, creative, and confident. "
                        "Never mention retrievals, databases, or system context. "
                        "Use fashion terminology casually. detailed thinking off"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return json.dumps(payload).encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf8"))
        try:
            return response_json["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            if isinstance(response_json, dict) and "generated_text" in response_json:
                return response_json["generated_text"].strip()
            raise ValueError(
                f"Could not extract generated text. Raw response starts with: {str(response_json)[:200]}..."
            )


class CustomEmbeddingsContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, texts: List[str], model_kwargs: Dict[str, Any]) -> bytes:
        payload = {
            "input": texts,
            "model": EMBEDDING_PAYLOAD_MODEL_NAME,
            "input_type": EMBEDDING_INPUT_TYPE,
        }
        return json.dumps(payload).encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf8"))
        if isinstance(response_json, dict) and "data" in response_json:
            data_list = response_json["data"]
            if isinstance(data_list, list):
                embs = [d["embedding"] for d in data_list if "embedding" in d]
                if embs:
                    return embs
        raise ValueError("Could not extract embedding vectors from model response.")


def load_catalog_from_file(filepath: str) -> List[Dict[str, Any]]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            print(f"Loading product catalog from {filepath}...")
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load catalog: {e}")
        return []


def _pick(d: Dict[str, Any], *keys: str, default=None):
    for k in keys:
        if k in d and d[k] not in (None, "", [], {}):
            return d[k]
    return default


def normalize_for_frontend(prod: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(_pick(prod, "id", "product_id", "asin", default="")),
        "title": _pick(prod, "title", "name", "product_title", default="Untitled Product"),
        "url": _pick(prod, "url", "link", "href", "product_url", default=""),
        "image": _pick(prod, "image", "image_url", "thumbnail", "thumb", "img", default=None),
        "price": str(_pick(prod, "price", "price_text", "amount", default="")),
        "rating": _pick(prod, "rating", "stars", default=None),
        "color": _pick(prod, "color", "colour", default=None),
        "size": _pick(prod, "size", default=None),
        "category": _pick(prod, "category", "cat", default=None),
        "product_details": _pick(
            prod, "product_details", "Product_Details", "details", "description", "caption", default=""
        ),
    }


def _doc_text_from_product(prod: Dict[str, Any]) -> str:
    p = normalize_for_frontend(prod)
    fields = [
        ("title", p.get("title", "")),
        ("product_details", p.get("product_details", "")),
        ("category", p.get("category", "")),
        ("color", p.get("color", "")),
        ("size", p.get("size", "")),
        ("price", "" if not p.get("price") else str(p["price"])),
        ("rating", "" if not p.get("rating") else str(p["rating"])),
    ]
    return " , ".join(f"{k}: {v}".strip() for k, v in fields if str(v).strip() != "")


def build_documents(catalog: List[Dict[str, Any]]) -> List[Document]:
    docs: List[Document] = []
    print("\n--- INDEXING LOG: EMBEDDING INPUT TEXTS ---")
    for i, prod in enumerate(catalog, start=1):
        text = _doc_text_from_product(prod)
        pid = str(prod.get("id", ""))
        preview = text.replace("\n", " | ")
        print(f"[{i}] [ID {pid}] EMBEDDING INPUT: {preview[:140]}...")
        docs.append(Document(page_content=text, metadata=prod))
    print("--- END INDEXING LOG ---\n")

    try:
        with open("documents.json", "w", encoding="utf-8") as f:
            json.dump([{"page_content": d.page_content, "metadata": d.metadata} for d in docs],
                      f, ensure_ascii=False, indent=2)
        print("✅ Saved documents.json")
    except Exception as e:
        print(f"[WARN] Could not write documents.json: {e}")

    if not docs:
        raise ValueError("No valid products to index.")
    return docs


def format_docs_for_llm(docs: List[Document]) -> str:
    return "\n---\n".join(doc.page_content for doc in docs)


def extract_full_products(docs: List[Document]) -> List[Dict[str, Any]]:
    return [doc.metadata for doc in docs]


STYLIST_FIRST_TURN_PROMPT = """You are a warm, concise fashion stylist.

Using only the CONTEXT (product details) and the USER QUESTION, suggest one cohesive outfit idea.
Keep it one paragraph (4–6 sentences, under ~120 words). Include: a top, a bottom, shoes,
an optional outer layer, and 1–2 accessories. Tie colors to the occasion/season if stated.
If the question implies size/fit, add one quick fit tip. Do not mention products, retrieval,
or databases.

CONTEXT:
{context}

USER QUESTION:
{question}

STYLIST:"""

# CONTEXT:
# {context}
STYLIST_WITH_CHAT_PROMPT = """You are a warm, concise fashion stylist.

Use the CHAT HISTORY to answer the USER QUESTION as the next turn in an ongoing chat.
Do not mention products, retrieval, or databases. Keep it one paragraph (4–6 sentences, under ~120 words).
Suggest: a top, a bottom, shoes, optional outer layer, and 1–2 accessories. Tie colors to the occasion/season.
If size/fit hints exist in the chat, add one quick fit tip. Be friendly and confident.

CHAT HISTORY (most recent last):
{chat}

USER QUESTION:
{question}

STYLIST:"""


def get_rag_chains(catalog: List[Dict[str, Any]]) -> Tuple[Runnable, Runnable, FAISS]:
    if not catalog:
        print("Error: Catalog is empty. Cannot initialize RAG chain.")
        return None, None, None

    print("--- Initializing Embeddings and LLM ---")
    documents = build_documents(catalog)

    embeddings_handler = CustomEmbeddingsContentHandler()
    sagemaker_embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=EMBEDDING_ENDPOINT_NAME,
        region_name=AWS_REGION,
        content_handler=embeddings_handler,
    )

    print(f"Indexing {len(documents)} products into FAISS...")
    vectorstore = FAISS.from_documents(documents, sagemaker_embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    llm_handler = CustomChatContentHandler()
    sagemaker_llm = SagemakerEndpoint(
        endpoint_name=LLM_ENDPOINT_NAME,
        region_name=AWS_REGION,
        model_kwargs={"max_tokens": 512},
        content_handler=llm_handler,
    )

    # --- First Turn ---
    llm_first_turn = PromptTemplate.from_template(STYLIST_FIRST_TURN_PROMPT) | sagemaker_llm | StrOutputParser()
    rag_chain_first = RunnableParallel({
        "llm_recommendation": (
                RunnableParallel({
                    "context": itemgetter("question") | retriever | format_docs_for_llm,
                    "question": itemgetter("question"),
                }) | llm_first_turn
        ),
        "products_json": itemgetter("question") | retriever | extract_full_products,
    })

    # --- Chat Turns ---
    llm_with_chat = PromptTemplate.from_template(STYLIST_WITH_CHAT_PROMPT) | sagemaker_llm | StrOutputParser()
    rag_chain_chat = RunnableParallel({
        "llm_recommendation": (
                RunnableParallel({
                    "context": itemgetter("question") | retriever | format_docs_for_llm,
                    "question": itemgetter("question"),
                    "chat": itemgetter("chat"),
                }) | llm_with_chat
        ),
        "products_json": itemgetter("question") | retriever | extract_full_products,
    })

    print("✅ RAG Chains (first-turn & chat-turn) ready.")
    return rag_chain_first, rag_chain_chat, vectorstore


try:
    from build_product_data import build_products_from_query
except Exception:
    def build_products_from_query(seed_query: str):
        print(f"[WARN] Using fallback build_products_from_query with seed: {seed_query!r}")
        path = DEFAULT_CATALOG_PATH
        return path, load_catalog_from_file(path)


def build_ranked_products(vectorstore: FAISS, query: str, k: int = TOP_K) -> List[Dict[str, Any]]:
    results = vectorstore.similarity_search_with_score(query, k=k)
    results = sorted(results, key=lambda x: x[1])
    ranked, seen = [], set()
    for doc, _ in results:
        meta = doc.metadata or {}
        pid = str(meta.get("id", ""))
        if pid not in seen:
            ranked.append(normalize_for_frontend(meta))
            seen.add(pid)
    return ranked


def _assemble_chat_prompt(
        chat_history_text: str, context_docs_text: str, question: str
) -> str:
    """Assembles the final text prompt using the STYLIST_WITH_CHAT_PROMPT template."""
    return STYLIST_WITH_CHAT_PROMPT.format(
        chat=chat_history_text, context=context_docs_text, question=question
    )


class ChatRAG:
    def __init__(self):
        self.chat_history: List[Tuple[str, str]] = []
        self.rag_chain_first: Optional[Runnable] = None
        self.rag_chain_chat: Optional[Runnable] = None
        self.vectorstore: Optional[FAISS] = None

    def _reindex_from_products(self, products: List[Dict[str, Any]]):
        self.rag_chain_first, self.rag_chain_chat, self.vectorstore = get_rag_chains(products)

    def _ensure_initialized(self, first_query: Optional[str] = None):
        if not self.rag_chain_first or not self.rag_chain_chat or not self.vectorstore:
            seed = (first_query or "").strip()
            path, products = build_products_from_query(seed, max_k=3, scrap_top_n=10, scrap_max_page=1)
            if not products:
                products = load_catalog_from_file(path) if path else []
            if not products:
                products = load_catalog_from_file(DEFAULT_CATALOG_PATH)
            if not products:
                raise RuntimeError("❌ Could not load or build product catalog.")
            self._reindex_from_products(products)

    def reset(self):
        self.chat_history.clear()
        self.rag_chain_first = None
        self.rag_chain_chat = None
        self.vectorstore = None

    @staticmethod
    def _history_to_text(history: List[Tuple[str, str]], max_turns: int = 8) -> str:
        tail = history[-max_turns:]
        if not tail:
            return "(no history)"
        lines = [f"User: {u}\nAssistant: {a}" for u, a in tail]
        return "\n".join(lines)

    def ask(self, user_message: str, k: int = TOP_K) -> Dict[str, Any]:
        initializing = not (self.rag_chain_first and self.rag_chain_chat and self.vectorstore)
        self._ensure_initialized(first_query=user_message if initializing else None)

        if not self.rag_chain_first or not self.rag_chain_chat:
            raise RuntimeError("RAG components not initialized.")

        is_first_turn = len(self.chat_history) == 0

        if is_first_turn:
            inputs = {"question": user_message}
            result = self.rag_chain_first.invoke(inputs)
        else:

            inputs = {"question": user_message, "chat": self._history_to_text(self.chat_history)}

            # 2. Invoke the chain to get the final components (context, history, question)
            # We use the RunnableParallel structure of the chain to get the exact parts
            # that will be assembled into the prompt.
            retrieval_result = RunnableParallel({
                "context": itemgetter("question") | self.vectorstore.as_retriever(
                    search_kwargs={"k": TOP_K}) | format_docs_for_llm,
                "question": itemgetter("question"),
                "chat": itemgetter("chat"),
            }).invoke(inputs)

            # 3. Assemble and Print the Final Prompt sent to the LLM
            final_llm_prompt = _assemble_chat_prompt(
                chat_history_text=retrieval_result['chat'],
                # context_docs_text=retrieval_result['context'],
                context_docs_text="",
                question=retrieval_result['question']
            )

            print("\n" + "=" * 20 + " FULL LLM PROMPT (TURN 2+) " + "=" * 20)
            print(final_llm_prompt)
            print("=" * 64 + "\n")

            result = self.rag_chain_chat.invoke(inputs)

        human_text = (result.get("llm_recommendation") or "").strip()
        ranked_products = build_ranked_products(self.vectorstore, user_message, k=k)
        self.chat_history.append((user_message, human_text or "(no answer)"))

        return {
            "human_recommendation": human_text,
            "products": ranked_products,
            "meta": {
                "used_history": not is_first_turn,
                "initialized_this_turn": initializing,
                "first_turn": is_first_turn,
            },
        }


chat_rag = ChatRAG()

if __name__ == "__main__":
    import json

    chat_rag.reset()

    turn_1 = "i want stylish shirt for mens age 20 size xl for winter wera"
    turn_2 = "and make it under 1500"
    turn_3 = "beige color one "

    print("\n" + "=" * 80)
    print("[TURN 1]")
    print(f"USER QUERY: {turn_1}\n")

    r1 = chat_rag.ask(turn_1)
    print("HUMAN RECOMMENDATION (LLM TEXT):")
    print(r1["human_recommendation"])
    print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
    print(json.dumps(r1["products"], ensure_ascii=False, indent=2))

    # 3
    print("\n" + "=" * 80)
    print("[TURN 2]")
    print(f"USER QUERY: {turn_2}\n")

    r2 = chat_rag.ask(turn_2)
    print("HUMAN RECOMMENDATION (LLM TEXT):")
    print(r2["human_recommendation"])
    print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
    print(json.dumps(r2["products"], ensure_ascii=False, indent=2))

    # 3
    print("\n" + "=" * 80)
    print("[TURN 3]")
    print(f"USER QUERY: {turn_3}\n")

    r3 = chat_rag.ask(turn_3)
    print("HUMAN RECOMMENDATION (LLM TEXT):")
    print(r3["human_recommendation"])
    print("\nPROGRAMMATIC PRODUCT DATA (JSON for Frontend, Ranked by Relevance):")
    print(json.dumps(r3["products"], ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("✅ Conversation complete.\n")
