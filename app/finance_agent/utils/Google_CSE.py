# tools/google_cse_tool.py
from __future__ import annotations
import os
import re
import html
from typing import List, Dict, Optional, Tuple
import httpx
from httpx import HTTPStatusError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

GOOGLE_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

# ---------- Helpers for contact extraction ----------
# Match Macau phone numbers in various formats:
# - 28123456 or 66123456 (8 digits, standard fixed/mobile)
# - 2812 3456 or 6612 3456 (with space separator)
# - 2812-3456 or 6612-3456 (with dash separator)
# - +853 2812 3456 or 853-2812-3456 (with country code)
# - 8989 0029 or 8896 0088 (toll-free numbers with space)
MACAU_PHONE = re.compile(
    r"(?:\+?853[\s\-]?)?"  # Optional country code +853 or 853
    r"(?:"
        r"(?:28|66)\d{2}[\s\-]?\d{4}|"  # Fixed line (28xx-xxxx) or mobile (66xx-xxxx) - 8 digits total
        r"(?:8989|8896)[\s\-]?\d{4}"  # Toll-free numbers (8989-xxxx or 8896-xxxx) - 8 digits total
    r")",
    re.IGNORECASE
)
ADDR_HINTS = ("地址", "地點", "位置", "Add:", "Address", "地址：", "電話", "Tel", "電話：")
# Pattern to extract address: street name + number + optional floor/unit
ADDR_PATTERN = re.compile(r'([^\s:：]+(?:街|路|大馬路|馬路|巷|道)\d+(?:號|号)(?:[^:：\n]{0,20})?)', re.UNICODE)


def _normalize_phone(phone: str) -> str:
    """
    Normalize phone number by removing all non-digit characters except leading +.
    Example: '2831 4986. mark. 28314986' -> '28314986'
    Example: '+853 2831 4986' -> '+85328314986'
    """
    if not phone:
        return phone

    # Keep only the first occurrence if duplicated
    parts = phone.split()
    if len(parts) > 1:
        # Find the first valid 8-digit phone number
        for part in parts:
            digits_only = re.sub(r'[^\d]', '', part)
            if len(digits_only) == 8:
                phone = part
                break

    # Remove all spaces, dashes, dots, and other non-digit characters except leading +
    if phone.startswith('+'):
        normalized = '+' + re.sub(r'[^\d]', '', phone[1:])
    else:
        normalized = re.sub(r'[^\d]', '', phone)

    return normalized


def _normalize_address(address: str) -> str:
    """
    Normalize address by keeping only Chinese characters, digits, and building/floor markers.
    Removes ALL English/Portuguese text completely.
    Example: '菜園涌邊街濠江花園第2座18樓A: Marg Canal Hortas Hou Kong Gdn bl 2 18° A: 電話：28314986. mark. downLoad'
             -> '菜園涌邊街濠江花園第2座18樓A'
    """
    if not address:
        return address

    # Split by colon and take the first part (usually the Chinese part)
    parts = re.split(r'[:：]', address)
    if parts:
        address = parts[0].strip()

    # Remove phone numbers from address
    address = MACAU_PHONE.sub('', address)

    # Remove ALL English/Portuguese words and markers
    # Keep only: Chinese characters (including traditional/simplified), digits, and specific floor/unit markers
    # This regex keeps: 中文字符 + digits + Chinese floor markers (樓/座/號/室/層/期/幢/棟 etc.)
    # Remove everything else including: English letters, dots, degree symbols, etc.
    cleaned_parts = []
    current_chinese = ""

    for char in address:
        # Keep Chinese characters (CJK Unified Ideographs)
        if '\u4e00' <= char <= '\u9fff':
            current_chinese += char
        # Keep digits
        elif char.isdigit():
            current_chinese += char
        # Keep single uppercase letter at end (for unit like "A", "B", etc.)
        elif char.isupper() and len(char) == 1:
            # Only keep if it's likely a unit marker (preceded by floor number)
            if current_chinese and (current_chinese[-1].isdigit() or current_chinese[-1] in '樓座室層'):
                current_chinese += char
        else:
            # Skip all other characters (English words, punctuation, etc.)
            continue

    address = current_chinese

    # Remove trailing markers and everything after
    address = re.sub(r'(電話|Tel|Phone|Add|Address|地址|mark|downLoad).*$', '', address, flags=re.IGNORECASE)

    return address.strip()

def _extract_from_text(text: str, debug: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """Extract address and phone number candidates from a snippet or page text."""
    text = html.unescape(text or "")
    phone_match = MACAU_PHONE.search(text)
    phone = phone_match.group(0) if phone_match else None

    # First try regex pattern matching for addresses
    addr_matches = ADDR_PATTERN.findall(text)
    if addr_matches:
        if debug:
            print(f"DEBUG: Regex found address matches: {addr_matches}")
        # Pick the shortest match as it's likely most specific
        addr = min(addr_matches, key=len).strip()
        # Clean up address by removing trailing "電話" or "Tel" markers
        addr = re.sub(r'(電話|Tel)[:：]?\s*$', '', addr, flags=re.IGNORECASE).strip()
        if debug:
            print(f"DEBUG: Selected address from regex (before normalization): {addr}")
            print(f"DEBUG: Phone (before normalization): {phone}")

        # Apply normalization
        addr = _normalize_address(addr) if addr else None
        phone = _normalize_phone(phone) if phone else None

        if debug:
            print(f"DEBUG: Normalized address: {addr}")
            print(f"DEBUG: Normalized phone: {phone}")
        return addr, phone

    # Fallback to line-by-line matching
    candidates = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if any(h in line for h in ADDR_HINTS) or line.endswith(("號", "樓", "室", "層", "大馬路", "馬路")):
            if 4 <= len(line) <= 100:
                candidates.append(line)
                if debug:
                    print(f"DEBUG: Found address candidate: {line}")

    addr = min(candidates, key=len) if candidates else None

    # Apply normalization
    addr = _normalize_address(addr) if addr else None
    phone = _normalize_phone(phone) if phone else None

    if debug:
        print(f"DEBUG: Total line candidates: {len(candidates)}, Selected and normalized: {addr}")
        print(f"DEBUG: Normalized phone: {phone}")
    return addr, phone


def _pick_from_items(items: List[Dict], debug: bool = False) -> Optional[Dict]:
    """Try extracting address and phone directly from snippets."""
    best_result = None
    fallback_result = None

    for it in items:
        addr, phone = _extract_from_text(it.get("snippet") or "", debug=debug)
        if addr and phone:
            # Found both - return immediately
            return {"address": addr, "phone": phone, "source": it.get("link")}
        elif addr or phone:
            # Found one - save as fallback if we don't have one yet
            if not fallback_result:
                fallback_result = {"address": addr, "phone": phone, "source": it.get("link")}

    return fallback_result

# ---------- Google CSE Core ----------
def _auth():
    api_key = os.getenv("CUSTOM_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cx:
        raise RuntimeError("Missing CUSTOM_SEARCH_API_KEY/GOOGLE_API_KEY or GOOGLE_CSE_ID env vars.")
    return api_key, cx


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def _hit_google_cse(params: dict) -> dict:
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(GOOGLE_CSE_ENDPOINT, params=params)
            r.raise_for_status()
            return r.json()
    except HTTPStatusError as e:
        try:
            print("DEBUG:", e.response.json())
        except Exception:
            print("DEBUG_RAW:", e.response.text)
        raise


def google_cse_search(q: str, num: int = 5, gl: str = "us", lr: str = "lang_en", safe: str = "off") -> List[dict]:
    """Returns a list of {title, link, snippet, source='google_cse'} dicts."""
    api_key, cx = _auth()
    num = max(1, min(10, num))
    params = {
        "key": api_key,
        "cx": cx,
        "q": q,
        "num": num,
        "gl": gl,
        "lr": lr,
        "safe": safe,
        "fields": "items(title,link,snippet)",
    }
    data = _hit_google_cse(params)
    items = data.get("items", []) or []
    return [
        {
            "title": it.get("title"),
            "link": it.get("link"),
            "snippet": it.get("snippet"),
            "source": "google_cse",
        }
        for it in items
    ]

# ---------- High-level helper ----------
def search_company_contact(name: str, fetch_fallback: bool = True, debug: bool = False) -> Dict[str, Optional[str]]:
    """
    Returns {'address': str|None, 'phone': str|None, 'source': str|None}
    Example:
        search_company_contact("長聯建築工程有限公司")
    """
    # Expanded search to include more Macau business listing sites
    q = f"{name} 電話 地址 (site:yp.mo OR site:google.com/maps OR site:facebook.com OR site:macaopage.com OR site:macauhub.com.mo)"
    items = google_cse_search(q=q, num=5, gl="MO", lr="lang_zh-TW")

    if debug:
        print(f"DEBUG: Found {len(items)} search results")
        for i, it in enumerate(items):
            print(f"DEBUG: Result {i+1}: {it.get('title')} - {it.get('link')}")
            print(f"DEBUG: Snippet: {it.get('snippet')}")

    hit = _pick_from_items(items, debug=debug)
    if hit and (hit["address"] or hit["phone"]):
        if debug:
            print(f"DEBUG: Found in snippet - Address: {hit['address']}, Phone: {hit['phone']}")
        return hit

    if not fetch_fallback or not items:
        if debug:
            print("DEBUG: No fallback or no items, returning None")
        return {"address": None, "phone": None, "source": None}

    # fallback: fetch the first few pages and parse for text
    if debug:
        print("DEBUG: Trying fallback - fetching actual webpages...")
    for i, it in enumerate(items[:3]):
        try:
            if debug:
                print(f"DEBUG: Fetching page {i+1}: {it['link']}")
            with httpx.Client(follow_redirects=True, timeout=15) as client:
                r = client.get(it["link"], headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                addr, phone = _extract_from_text(r.text, debug=debug)
                if addr or phone:
                    if debug:
                        print(f"DEBUG: Found on page - Address: {addr}, Phone: {phone}")
                    return {"address": addr, "phone": phone, "source": it["link"]}
        except Exception as e:
            if debug:
                print(f"DEBUG: Error fetching page: {e}")
            continue

    return {"address": None, "phone": None, "source": None}



