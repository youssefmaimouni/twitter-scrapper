#!/usr/bin/env python3
import asyncio
import sys
import os

# Fix Windows unicode output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from scraper import scrape_twitter

# Helper to extract followers/following from result with common key names
def extract_list(result, keys):
    for k in keys:
        if k in result and isinstance(result[k], (list, tuple)):
            return result[k]
    return None

async def fetch_user(username, max_followers=100, max_following=100, show=20):
    try:
        print(f"\nStarting fetch for @{username}")
        print(f"Requesting followers: {max_followers}, following: {max_following} (tweets will be skipped)")

        result = await scrape_twitter(
            username=username,
            max_tweets=0,
            max_retweets=0,
            max_followers=max_followers,
            max_following=max_following
        )

        # Extract followers and following lists
        followers = extract_list(result, ['followers', 'followers_list', 'followers_data', 'followers_users'])
        following = extract_list(result, ['following', 'following_list', 'friends', 'following_data', 'following_users'])

        # Print profile summary
        profile = result.get('user_profile') or result.get('profile') or {}
        print("Profile summary:")
        if profile:
            print("  username:", profile.get('username') or profile.get('screen_name') or username)
            if 'name' in profile:
                print("  name:", profile.get('name'))
            if 'bio' in profile:
                print("  bio:", profile.get('bio'))
            if 'followers_count' in profile:
                print("  followers_count:", profile.get('followers_count'))
            if 'following_count' in profile:
                print("  following_count:", profile.get('following_count'))
        else:
            print("  (no profile data returned)")

        # Utility to print lists
        def print_list(name, data):
            if data is None:
                print(f"\n{name}: (not present in result)")
                return
            print(f"\n{name}: total returned = {len(data)}; showing up to {show}:")
            for i, item in enumerate(data[:show], start=1):
                if isinstance(item, dict):
                    u = item.get('username') or item.get('screen_name') or item.get('handle') or item.get('user') or item.get('name')
                    extra = []
                    if 'id' in item:
                        extra.append(f"id={item.get('id')}")
                    if 'followers_count' in item:
                        extra.append(f"foll={item.get('followers_count')}")
                    tag = f" ({', '.join(extra)})" if extra else ""
                    print(f"  {i}. {u or str(item)}{tag}")
                else:
                    print(f"  {i}. {item}")
            if len(data) > show:
                print(f"  ... (+{len(data)-show} more)")

        print_list("Followers", followers)
        print_list("Following", following)

        # Save JSON
        output_folder = os.path.join(os.path.dirname(__file__), "scraped_profiles")
        os.makedirs(output_folder, exist_ok=True)
        filepath = os.path.join(output_folder, f"{username}.json")
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\nProfile saved to {filepath}")
        return True

    except Exception as e:
        print(f"Failed to fetch @{username}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    # List of usernames to scrape
    usernames = ["elonmusk", "barackobama", "cristiano", "realDonaldTrump"]

    # Loop through usernames sequentially
    for u in usernames:
        await fetch_user(u)

if __name__ == "__main__":
    asyncio.run(main())
