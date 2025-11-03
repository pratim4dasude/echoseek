import json, re
from typing import List, Dict, Any, Tuple

from llm_standaloe_langcahin import llm_chat
from scarpper_products import amazom_scraper_working


def _parse_keywords_from_contex(contex: str, max_k: int = 3) -> List[str]:
    if not contex:
        return []

    text = contex.strip().strip("[]{}()\"' ")
    parts = re.split(r"[,\n]|•|- ", text)
    parts = [re.sub(r"\s+", " ", p).strip() for p in parts if p and p.strip()]

    seen = set()
    out: List[str] = []
    for p in parts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            out.append(p)

    return out[:max_k]


def _dedupe_products(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen_urls, seen_ids = set(), set()

    for it in items:
        if not isinstance(it, dict):
            continue

        # Check common keys for URL
        url = str(it.get("url") or it.get("link") or it.get("product_url") or "").strip()
        pid = str(it.get("id") or "").strip()

        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)
        elif pid:
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
        else:
            # Skip if neither URL nor ID is available for tracking
            continue

        deduped.append(it)

    return deduped


def reindex_products(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    for i, product in enumerate(items):
        product['id'] = i + 1
    return items


def build_products_from_query(user_query: str, out_file: str = "products.json", max_k=3, scrap_top_n=3,
                              scrap_max_page=1) -> Tuple[str, List[Dict[str, Any]]]:
    # wrapped = (
    #     "Extract ONLY the most important e-commerce search keywords (3–6 short phrases). "
    #     "Return them as comma-separated phrases No explanations.\n\n"
    #     f"User Query:\n{user_query}\n"
    # )

    wrapped = (
        "You are a keyword generator for Amazon-style product search.\n"
        "From the user's text, extract 4–7 SHORT keyword phrases optimized for e-commerce search.\n"
        "Focus on: category and key modifiers (gender, size, color, fit, occasion, pattern, fabric, price tier if stated).\n"
        "RULES:\n"
        "- Lowercase only. No punctuation except commas as separators.\n"
        "- Phrases of 2–5 words each. No explanations, no numbering.\n"
        "- Prefer category-first phrasing (e.g., \"men formal shirt xl\", \"blue party shirt men\").\n"
        "- Include only what is implied or stated (no hallucinated brands/models).\n"
        "- If size exists, include it in relevant apparel phrases (e.g., xl).\n"
        "- If occasion exists (party, wedding, office), include an occasion variant.\n"
        "- If color exists, include a color variant.\n"
        "- If user intent is broad (e.g., full outfit), include top adjacent categories (e.g., shirt, trousers, blazer) as separate phrases.\n"
        "- Output MUST be a single line of comma-separated phrases.\n\n"
        "User text:\n"
        f"{user_query}\n\n"
        "Keywords:"
    )



    resp = llm_chat(wrapped)
    contex_text = ""
    if isinstance(resp, dict):
        contex_text = str(resp.get("contex", "")).strip()
    else:
        contex_text = str(resp).strip()

    if contex_text and "error occur -" not in contex_text.lower() and "no output decided" not in contex_text.lower():
        keywords = _parse_keywords_from_contex(contex_text, max_k=max_k)
    else:
        keywords = []

    # keywords = _parse_keywords_from_contex(contex_text, max_k=max_k)

    if not keywords:
        keywords = [user_query]

    print(f"Keywords: {keywords}")

    all_items: List[Dict[str, Any]] = []
    for kw in keywords:
        try:
            batch = amazom_scraper_working(kw, scrap_max_page, scrap_top_n)
            if isinstance(batch, list):
                all_items.extend(batch)
            print(f"  + {kw}: {len(batch) if isinstance(batch, list) else 0} items")
        except Exception as e:
            print(f"  ! {kw}: scrape failed -> {e}")

    if not all_items:
        raise ValueError("No products scraped for any keyword.")

    merged = _dedupe_products(all_items)
    final_json = reindex_products(merged)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(final_json)} products to {out_file}")
    return out_file, final_json


if __name__ == "__main__":
    try:
        path, products = build_products_from_query("I need a matching women dress for a party")
        print(path, len(products))
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
