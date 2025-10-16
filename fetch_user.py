#!/usr/bin/env python3
import asyncio
import sys
import os
from datetime import datetime
import json
from fetch_images import get_photo_image_url

# Fix Windows unicode output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from scraper import scrape_twitter

def extract_list(result, keys):
    for k in keys:
        if k in result and isinstance(result[k], (list, tuple)):
            return result[k]
    return None

async def fetch_user(username, max_tweets=20, max_followers=100, max_following=100, show=20, stop_date=None):
    try:
        print(f"\nStarting fetch for @{username}")
        print(f"Requesting tweets: {max_tweets}, followers: {max_followers}, following: {max_following}")

        result = await scrape_twitter(
            username=username,
            max_tweets=max_tweets,
            max_retweets=0,
            max_followers=max_followers,
            max_following=max_following,
            stop_date=stop_date
        )

        # Fetch profile image URL
        print(f"Fetching profile image for @{username} ...")
        image_url = await get_photo_image_url(username)
        result["profile_image_url"] = image_url

        # Extract lists
        followers = extract_list(result, ['followers', 'followers_list', 'followers_data', 'followers_users'])
        following = extract_list(result, ['following', 'following_list', 'friends', 'following_data', 'following_users'])
        tweets = extract_list(result, ['tweets', 'user_tweets', 'tweets_data'])

        # Profile summary
        profile = result.get('user_profile') or result.get('profile') or {}
        print("Profile summary:")
        if profile:
            print("  username:", profile.get('username') or profile.get('screen_name') or username)
            print("  name:", profile.get('name', ''))
            print("  bio:", profile.get('bio', ''))
            print("  followers_count:", profile.get('followers_count', 0))
            print("  following_count:", profile.get('following_count', 0))
        else:
            print("  (no profile data returned)")

        # Print utility
        def print_list(name, data):
            if not data:
                print(f"\n{name}: (not present in result)")
                return
            print(f"\n{name}: total returned = {len(data)}; showing up to {show}:")
            for i, item in enumerate(data[:show], start=1):
                if isinstance(item, dict):
                    u = item.get('username') or item.get('screen_name') or item.get('handle') or item.get('user') or item.get('name')
                    text = item.get('text') if 'text' in item else ''
                    extra = []
                    if 'id' in item: extra.append(f"id={item.get('id')}")
                    if 'followers_count' in item: extra.append(f"foll={item.get('followers_count')}")
                    tag = f" ({', '.join(extra)})" if extra else ""
                    print(f"  {i}. {u or text}{tag}")
                    if text: print(f"     -> {text}")
                else:
                    print(f"  {i}. {item}")
            if len(data) > show:
                print(f"  ... (+{len(data)-show} more)")

        print_list("Tweets", tweets)
        print_list("Followers", followers)
        print_list("Following", following)

        # Save JSON
        output_folder = os.path.join(os.path.dirname(__file__), "scraped_profiles")
        os.makedirs(output_folder, exist_ok=True)
        filepath = os.path.join(output_folder, f"{username}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\nProfile saved to {filepath}")
        return True

    except Exception as e:
        print(f"Failed to fetch @{username}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def is_scraped(username, output_folder):
    path = os.path.join(output_folder, f"{username}.json")
    if not os.path.exists(path):
        return False
    try:
        if os.path.getsize(path) < 10:
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # consider as processed if there's useful content or a skipped marker
        if isinstance(data, dict) and (data.get("skipped") or data.get("profile_image_url") or data.get("user_profile") or data.get("tweets")):
            return True
        return True  # fallback: file exists and non-empty => treated as processed
    except Exception:
        return False
    
async def main():
    import json

    with open("users_extended.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    usernames = [entry["Twitter Username"] for entry in data]
    for username in usernames:
        print(username)

    #usernames = usernames[:3]  
    stop_date = datetime(2025, 1, 1).date()  # optional: stop at this date

    output_folder = os.path.join(os.path.dirname(__file__), "scraped_profiles")
    os.makedirs(output_folder, exist_ok=True)
    for u in usernames:
        if is_scraped(u, output_folder):
            print(f"Already scraped or attempted {u}, skipping.")
            continue
        await fetch_user(u, max_tweets=10, max_followers=100, max_following=100, show=5, stop_date=stop_date)

if __name__ == "__main__":
    asyncio.run(main())
