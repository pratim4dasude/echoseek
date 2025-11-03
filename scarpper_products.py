from selenium.webdriver.common.keys import Keys
import json, re, time, random
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from typing import List, Dict, Union

import time
from typing import List, Dict
import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")

def scrape_amazon_links(
        base_url="https://www.amazon.in",
        keyword="t-shirt",
        max_pages=None,
        per_page=None,
        top_n=None,
        headless=True,
        timeout=300
):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1280,1600")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, timeout)
    seen, data, page = set(), [], 0

    try:
        driver.get(base_url)
        wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        box = driver.find_element(By.ID, "twotabsearchtextbox")
        box.clear()
        box.send_keys(keyword)
        box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(3.0, 5.0))

        while True:
            if _looks_like_captcha(driver):
                print("\n CAPTCHA detected! Cannot proceed with scraping.")
                return []
            page += 1
            print(f"\n Scraping page {page} ...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.0)

            collected_this_page = 0
            for a in driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-no-outline']"):
                href = a.get_attribute("href")
                if not href or href in seen:
                    continue
                seen.add(href)
                data.append({"id": len(data) + 1, "link": href})
                collected_this_page += 1

                if top_n and len(data) >= top_n:
                    print(f" Reached top {top_n} links. Stopping.")
                    # if out_file:
                    #     with open(out_file, "w", encoding="utf-8") as f:
                    #         json.dump(data, f, indent=2, ensure_ascii=False)
                    driver.quit()
                    # print(f"💾 Saved {len(data)} links to {out_file}")
                    return data

                if per_page and collected_this_page >= per_page:
                    break

            print(f" Page {page} done — total links so far: {len(data)}")

            if max_pages and page >= max_pages:
                print(f" Reached max page limit ({max_pages}). Stopping.")
                break

            next_btns = driver.find_elements(By.CSS_SELECTOR, "a.s-pagination-next:not(.s-pagination-disabled)")
            if not next_btns:
                print(" No more pages found. Stopping.")
                break

            next_btns[0].click()
            time.sleep(1.0)

    finally:
        # if out_file:
            # with open(out_file, "w", encoding="utf-8") as f:
            #     json.dump(data, f, indent=2, ensure_ascii=False)
        driver.quit()

    print(f"\n Scraping complete — total pages: {page}, total links: {len(data)}")
    # print(f"Data saved to {out_file}")
    return data


def _text_or_none(el) -> Optional[str]:
    try:
        t = el.text.strip()
        return t if t else None
    except Exception:
        return None


def _find_first(driver, selectors: List[str]) -> Optional[str]:

    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            txt = _text_or_none(el)
            if txt:
                return txt
        except NoSuchElementException:
            continue
    return None


def _attr_of_first(driver, selectors: List[str], attr: str) -> Optional[str]:
    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            val = el.get_attribute(attr)
            if val:
                return val
        except NoSuchElementException:
            continue
    return None


def _parse_price_from_container_text(txt: str) -> Optional[str]:

    if not txt:
        return None
    m = re.search(r"₹\s?[\d,]+(?:\.\d{1,2})?", txt)
    return m.group(0) if m else None


def _parse_rating(txt: Optional[str]) -> Optional[float]:

    if not txt:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", txt)
    try:
        return float(m.group(1)) if m else None
    except Exception:
        return None


def _looks_like_captcha(driver) -> bool:
    try:
        if "Enter the characters you see" in driver.page_source or "captchacharacters" in driver.page_source:
            return True
    except Exception:
        pass
    return False


def _clean_variation(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    v = val.strip()
    if v.lower().startswith("select"):
        return None
    return v


def _extract_twister_selection(driver, dim_key: str) -> Optional[str]:
    sel = _find_first(driver, [
        f"[id*='inline-twister-expanded-dimension-text-{dim_key}'] .a-text-bold",
        f"span[id*='inline-twister-expanded-dimension-text-{dim_key}']",
        f"div[id*='inline-twister-expanded-dimension-text-{dim_key}']",
    ])
    if sel:
        return sel

    sel = _find_first(driver, [
        f"div[id*='inline-twister-singleton-header-{dim_key}'] span.inline-twister-dim-title-value",
        f"div[id*='inline-twister-singleton-header-{dim_key}'] span.inline-twister-dim-title-value-truncate",
        f"div[id*='inline-twister-singleton-header-{dim_key}'] .a-text-bold",
    ])
    if sel:
        return sel

    sel = _find_first(driver, [
        f"div[id*='inline-twister-dim-title-{dim_key}'] + span",
        f"div[id*='inline-twister-row-{dim_key}'] span.inline-twister-dim-title-value",
        f"div[id*='inline-twister-row-{dim_key}'] .inline-twister-dim-title-value-truncate",
        f"div[id*='inline-twister-row-{dim_key}'] .a-text-bold",
    ])
    if sel:
        return sel

    try:
        hdr = driver.find_element(By.CSS_SELECTOR, f"div[id*='inline-twister-expander-header-{dim_key}']")
        aria = (hdr.get_attribute("aria-label") or "").strip()
        if " is " in aria:
            val = aria.split(" is ", 1)[1].split(".")[0].strip()
            if val:
                return val
    except NoSuchElementException:
        pass

    return None


def _extract_category(driver, drop_first: bool = True, joiner: str = " > ") -> Optional[str]:
    try:
        cont = driver.find_element(By.CSS_SELECTOR, "div[id*='wayfinding-breadcrumbs_feature_div']")
    except NoSuchElementException:
        return None

    # Primary: all breadcrumb anchors inside the list
    links = cont.find_elements(By.CSS_SELECTOR, "ul a.a-link-normal")
    labels = [(_text_or_none(a) or "").strip() for a in links]
    labels = [x for x in labels if x]  # remove empties

    if not labels:
        return None

    if drop_first and len(labels) >= 2:
        labels = labels[1:]

    return joiner.join(labels) if labels else None


def get_price(s: str):
    if not s: return ""
    m = re.search(r"[\d.,]+(?:\.\d{1,2})?", s)
    if not m: return ""
    n = m.group(0).replace(",", "")
    return int(n) if "." not in n else float(n)


def scrape_product_fields(driver, url: str, wait: WebDriverWait) -> Dict[str, Optional[str]]:
    driver.get(url)

    try:
        WebDriverWait(driver, wait._timeout).until(
            lambda d: _looks_like_captcha(d) or d.find_elements(
                By.CSS_SELECTOR, "#productTitle, h1 span.a-size-large.product-title-word-break"
            )
        )
    except TimeoutException:
        pass

    if _looks_like_captcha(driver):
        return {
            "title": None, "price": None, "rating": None, "image": None,
            "color": None, "size": None, "category": None, "captcha": True
        }

    # Title
    title = _find_first(driver, [
        "#productTitle",
        "h1 span.a-size-large.product-title-word-break",
        "span#title #productTitle",
        "h1#title"
    ])

    # Price
    price = None
    if not price:
        price_whole = _find_first(driver, [
            "#corePriceDisplay_desktop_feature_div .a-price .a-price-whole",
            ".a-price .a-price-whole"
        ])
        price_symbol = _find_first(driver, [
            "#corePriceDisplay_desktop_feature_div .a-price .a-price-symbol",
            ".a-price .a-price-symbol"
        ])
        price_frac = _find_first(driver, [
            "#corePriceDisplay_desktop_feature_div .a-price .a-price-fraction",
            ".a-price .a-price-fraction"
        ])
        if price_whole:
            symbol = price_symbol or "₹"
            frac = f".{price_frac}" if price_frac else ""
            price = f"{symbol}{price_whole}{frac}".replace("..", ".")

    if not price:
        legacy_price = _find_first(driver, [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#tp_price_block_total_price_ww",
            "#newBuyBoxPrice",
            "#sns-base-price",
            ".a-price .a-offscreen"
        ])
        if legacy_price:
            price = legacy_price
    if not price:
        price = _parse_price_from_container_text(
            _find_first(driver, ["#corePrice_feature_div", "#corePrice_desktop", ".apexPriceToPay", ".a-price"])
        )

    # Rating
    rating_text = (
            _find_first(driver, ["span[data-hook='rating-out-of-text']"])
            or _attr_of_first(driver, ["#acrPopover", "span#acrPopover"], "title")
            or _find_first(driver, ["span.arp-rating-out-of-text", "span#acrCustomerReviewText"])
    )
    rating = _parse_rating(rating_text)

    # Image
    image_url = _attr_of_first(driver, ["img#landingImage", "#imgTagWrapperId img", "img[data-old-hires]"], "src")

    color = _extract_twister_selection(driver, "color_name")
    size = _extract_twister_selection(driver, "size_name")

    # Fallback: Product Overview (po-*)
    if not color:
        color = _find_first(driver, [".po-color .a-span9 span", ".po-color .a-span9"])
    if not size:
        size = _find_first(driver, [".po-size .a-span9 span", ".po-size .a-span9"])

    if not color or not size:
        try:
            bullets = driver.find_elements(By.CSS_SELECTOR,"#detailBullets_feature_div li, #detailBulletsWrapper_feature_div li")
            for li in bullets:
                txt = (li.text or "").strip()
                if not txt:
                    continue
                if not color and ("Colour" in txt or "Color" in txt):
                    parts = txt.split(":", 1)
                    if len(parts) > 1:
                        color = parts[1].strip() or color
                if not size and "Size" in txt:
                    parts = txt.split(":", 1)
                    if len(parts) > 1:
                        size = parts[1].strip() or size
        except Exception:
            pass

    color = _clean_variation(color)
    size = _clean_variation(size)

    # Category from breadcrumbs (skip first crumb; join with spaces via " > ")
    category = _extract_category(driver, drop_first=True, joiner=" > ")

    price = str(get_price(price))

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "image": image_url,
        "color": color,
        "size": size,
        "category": category,
    }


def enrich_products(
        in_file: Union[str, List[Dict]],
        out_file: str = "products_detailed.json",
        headless: bool = True,
        per_item_delay_range=(1.2, 2.4),
        timeout: int = 15,
        limit: Optional[int] = None
):

    if isinstance(in_file, str):
        with open(in_file, "r", encoding="utf-8") as f:
            items = json.load(f)
    else:
        items = in_file

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1280,1600")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, timeout)

    enriched = []
    errors = 0

    try:
        for idx, row in enumerate(items, start=1):
            if limit and idx > limit:
                break

            url = row.get("link") or row.get("url")
            pid = row.get("id", idx)

            if not url:
                enriched.append({
                    "id": str(pid),
                    "title": None,
                    "url": None,
                    "image": None,
                    "price": None,
                    "rating": None,
                    "color": None,
                    "size": None,
                    "category": None,
                })
                continue

            print(f" [{idx}/{len(items)}] {url}")

            try:
                fields = scrape_product_fields(driver, url, wait)
            except (TimeoutException, WebDriverException) as e:
                errors += 1
                print(f" Error: {e.__class__.__name__} — {e}")
                fields = {
                    "title": None, "price": None, "rating": None, "image": None,
                    "color": None, "size": None, "category": None
                }

            enriched.append({
                "id": str(pid),
                "title": fields.get("title"),
                "url": url,
                "image": fields.get("image"),
                "price": fields.get("price"),
                "rating": fields.get("rating"),
                "color": fields.get("color"),
                "size": fields.get("size"),
                "category": fields.get("category"),
            })

            time.sleep(random.uniform(*per_item_delay_range))

    finally:
        # with open(out_file, "w", encoding="utf-8") as f:
        #     json.dump(enriched, f, indent=2, ensure_ascii=False)
        driver.quit()

    print(f"\n Done. Saved {len(enriched)} items to {out_file} (errors: {errors}).")
    return enriched


# ////////////////////////////////////////////


# //////////////////////////  OPEN AI WORKER ////////////////////////////////////


def load_image_as_pil(image_source: str) -> Image.Image:
    if image_source.lower().startswith(('http://', 'https://')):
        response = requests.get(image_source, stream=True)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    else:
        return Image.open(image_source)


def resize_and_encode_image(image_source: str, target_height: int) -> str:
    img = load_image_as_pil(image_source)
    original_width, original_height = img.size

    aspect_ratio = original_width / original_height
    new_width = int(target_height * aspect_ratio)
    new_size = (new_width, target_height)

    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

    buffered = BytesIO()
    resized_img.save(buffered, format="JPEG")

    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/jpeg;base64,{img_base64}"


def get_product_description_and_tokens(product_data: dict, instruction_prompt: str):

    MODEL_NAME = "gpt-5-nano"
    TARGET_HEIGHT = 512

    if not API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    metadata_prompt = (
        "PRODUCT METADATA:\n"
        f"Title: {product_data.get('title')}\n"
        f"Price: {product_data.get('price')}\n"
        f"Rating: {product_data.get('rating')}\n"
        f"Color: {product_data.get('color')}\n"
        f"Size: {product_data.get('size')}\n"
        f"Category: {product_data.get('category')}\n\n"
        "INSTRUCTION:\n"
        f"{instruction_prompt}"
    )

    print("-->\n", metadata_prompt)

    image_url = product_data.get('image')
    if not image_url:
        raise ValueError("Product data is missing an 'image' URL.")

    base64_image_data_url = resize_and_encode_image(image_url, TARGET_HEIGHT)

    client = OpenAI(api_key=API_KEY)

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": metadata_prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": base64_image_data_url
                    }
                ]
            }
        ]
    )

    return response.output_text, response.usage


def load_products(data_source: Union[str, List[Dict], Dict]) -> List[Dict]:
    data = data_source

    if isinstance(data_source, str):
        try:
            with open(data_source, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Could not load or parse file at {data_source}: {e}")

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "products" in data and isinstance(data["products"], list):
        return data["products"]

    raise ValueError(
        "Invalid data format. Input must be a file path, a list of product dicts, or a dict with a 'products' list."
    )


def save_products(path: str, products: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def enrich_products_openai(
        products: List[Dict],
        instruction_prompt: str,
        skip_if_present: bool = True
) -> List[Dict]:

    MODEL_NAME = "gpt-5-nano"
    PER_ITEM_SLEEP_SEC = 2

    enriched = []
    for idx, item in enumerate(products, start=1):
        title = item.get("title") or item.get("Title") or f"item-{idx}"
        print(f"\n[{idx}/{len(products)}] {title}")

        if skip_if_present and "product_details" in item and item["product_details"]:
            print("product_details present → skipping")
            enriched.append(item)
            continue

        try:
            text, usage = get_product_description_and_tokens(item, instruction_prompt)
            item["product_details"] = text.strip()

            item["_usage"] = {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
                "model": MODEL_NAME
            }

            print("✓ done | tokens:", item["_usage"])
        except Exception as e:
            item["product_details"] = ""
            item["_error"] = str(e)
            print("✗ error:", e)

        enriched.append(item)
        time.sleep(PER_ITEM_SLEEP_SEC)

    return enriched


def openaiworker(INPUT_JSON, OUTPUT_JSON="products_enriched.json"):

    instruction = (
        "Using the product metadata provided, describe in detail the main clothing item visible in the image. "
        "Focus on its visual attributes such as color, material, fit, length, type, and any visible design elements. "
        "You may naturally reference the given gender, size, and price in context, but do not mention the brand name, logos, model, or background. "
        "Write a 3–4 line paragraph in a clear, marketing-style tone that highlights the product’s look and appeal."
    )

    products = load_products(INPUT_JSON)
    enriched = enrich_products_openai(products, instruction_prompt=instruction, skip_if_present=True)
    # for item in enriched:
    #     item.pop("_usage", None)
    #     item.pop("_error", None)
    # save_products(OUTPUT_JSON, enriched)
    # print(f"\nSaved enriched file → {OUTPUT_JSON}")
    return enriched


# ////////////////////////// ^^^^^^^^^^^^^^^^^^^^^ OPEN AI WORKER  ^^^^^^^^^^^ ////////////////////////////////////

def amazom_scraper_working(keyword: str, max_pages: int, top_n: int, base_url="https://www.amazon.in/"):

    results = scrape_amazon_links(
        base_url=base_url,
        keyword=keyword,
        headless=True,
        max_pages=max_pages,
        top_n=top_n
    )

    print(f"\n>>>> Finished scraping {len(results)} links.\n")
    print("00000--->", results)

    r = enrich_products(
        in_file=results,
        headless=True,
        limit=None  # set an int while testing, e.g. 10
    )
    print(f"\n>>>> CAPTIONING  started \n")
    print("results ----->", r)
    product_categoryies = openaiworker(r)

    return product_categoryies


if __name__ == "__main__":
    k = amazom_scraper_working("women dress", 1, 3, "https://www.amazon.in/")
    print(k)
