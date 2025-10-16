import requests
import json
import re
import time
import sys
from typing import List, Dict

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv('serper_api_key')

if not API_KEY:
    raise ValueError("serper_api_key not found in environment variables")
SEARCH_URL = "https://google.serper.dev/search"
OUTPUT_FILE = "users_extended.json"  # existing file will be loaded and preserved

# --- user params ---
queries = [
    # 🌍 General Data & AI queries
    "data scientist maroc site:https://x.com/",
    "data engineer maroc site:https://x.com/",
    "machine learning maroc site:https://x.com/",
    "artificial intelligence maroc site:https://x.com/",
    "deep learning maroc site:https://x.com/",
    "data analyst maroc site:https://x.com/",
    "big data maroc site:https://x.com/",
    "business intelligence maroc site:https://x.com/",
    "analyste de données maroc site:https://x.com/",
    "scientifique des données maroc site:https://x.com/",
    
    # 💻 Broader tech & AI community
    "ai engineer maroc site:https://x.com/",
    "cloud engineer maroc site:https://x.com/",
    "data science student maroc site:https://x.com/",
    "phd data science maroc site:https://x.com/",
    "professeur data maroc site:https://x.com/",
    "developer ai maroc site:https://x.com/",
    "researcher ai maroc site:https://x.com/",
    "etudiant intelligence artificielle maroc site:https://x.com/",
    "formateur data maroc site:https://x.com/"
]

max_pages_per_query = 3   # how many pages to try per query (set to 1,2,3,...)
delay_between_requests = 1.0  # seconds (increase if rate limited)
location_context = "Casablanca, Casablanca-Settat, Morocco"  # optional location param sent to API
gl = "ma"
# --------------------

HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

username_re = re.compile(r"x\.com/([A-Za-z0-9_]+)")

def load_existing_users(path: str) -> List[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("Existing file is not a list — starting with empty list.")
                return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Warning: existing JSON file corrupt or empty. Back it up and restart.")
        return []

def save_users(path: str, users: List[Dict]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def infer_location(item: dict) -> str:
    # Basic heuristics: check snippet/title for known city names or 'Maroc'
    snippet = (item.get("snippet") or "").lower()
    title = (item.get("title") or "").lower()
    for city in ["casablanca"]:
        if city in snippet or city in title:
            # capitalize first letter
            return city.capitalize() + ", Morocco"
    if "maroc" in snippet or "morocco" in snippet:
        return "Morocco"
    return item.get("date") or "Unknown"

def extract_users_from_response(data: dict) -> List[Dict]:
    found = []
    for item in data.get("organic", []):
        link = item.get("link", "") or ""
        match = username_re.search(link)
        if not match:
            # sometimes the link uses http instead of https or 'www', try a looser regex on the link
            match = re.search(r"x\.com/([A-Za-z0-9_]+)", link)
        if match:
            username = match.group(1)
            loc = infer_location(item)
            entry = {
                "Twitter Username": username,
                "Location": loc,
                "source_title": item.get("title"),
                "source_snippet": item.get("snippet"),
                "source_link": link,
                "source_query_position": item.get("position")
            }
            found.append(entry)
    return found

def make_request(query: str, page: int = 1):
    payload = {
        "q": query,
        "gl": gl,
        # include location context if helpful
        "location": location_context,
        "page": page
    }
    # Serper might not support 'page' on all plans; if not, API may ignore it or return same results.
    resp = requests.post(SEARCH_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    existing = load_existing_users(OUTPUT_FILE)
    existing_usernames = {u["Twitter Username"].lower(): u for u in existing}
    total_added = 0

    for q in queries:
        for page in range(1, max_pages_per_query + 1):
            try:
                print(f"Searching query: {q!r}  — page {page}")
                data = make_request(q, page=page)
            except requests.HTTPError as e:
                print(f"HTTP error for query {q} page {page}: {e}. Retrying after backoff...")
                # simple backoff loop
                for attempt in range(1, 4):
                    wait = 2 ** attempt
                    time.sleep(wait)
                    try:
                        data = make_request(q, page=page)
                        break
                    except Exception as e2:
                        print(f"  Retry {attempt} failed: {e2}")
                else:
                    print("  All retries failed — skipping this page.")
                    continue
            except Exception as e:
                print(f"Error fetching page for query {q}: {e}. Skipping page.")
                continue

            new_entries = extract_users_from_response(data)
            added_this_page = 0
            for e in new_entries:
                uname_lower = e["Twitter Username"].lower()
                if uname_lower not in existing_usernames:
                    existing_usernames[uname_lower] = e
                    existing.append(e)
                    added_this_page += 1
                    total_added += 1

            if added_this_page:
                # Save progress immediately (append semantics preserved by loading prior file)
                save_users(OUTPUT_FILE, existing)
                print(f"  +{added_this_page} new users added (saved).")
            else:
                print("  No new users on this page.")

            # be polite / avoid rate limits
            time.sleep(delay_between_requests)

    print(f"Done. Total new users added this run: {total_added}. Output file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
