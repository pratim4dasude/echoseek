from typing import Dict, Any, List
from threading import Lock

from new_rag_convo_with_init import chat_rag

_init_lock = Lock()
_initialized = False


def _ensure_ready() -> None:
    global _initialized
    if _initialized:
        return
    with _init_lock:
        if not _initialized:
            chat_rag.reset()
            _initialized = True


def reset_state() -> None:
    global _initialized
    chat_rag.reset()
    _initialized = False


def _to_links(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []
    for i, p in enumerate(products, start=1):
        links.append({
            "id": str(p.get("id") or i),
            "title": p.get("title") or "Untitled Product",
            "url": p.get("url") or "#",
            "image": p.get("image"),
            "price": p.get("price"),
            "rating": p.get("rating"),
        })
    return links


def llm_chat(user_input: str) -> Dict[str, Any]:
    _ensure_ready()

    result = chat_rag.ask(user_input)
    text: str = (result.get("human_recommendation") or "").strip()
    products: List[Dict[str, Any]] = result.get("products") or []

    return {
        "text": text,
        "links": _to_links(products),
        "meta": result.get("meta", {}),
    }
