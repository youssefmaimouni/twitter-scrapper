#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from scraper import scrape_twitter

# Helper to extract followers/following from result with common key names
def extract_list(result, keys):
    for k in keys:
        if k in result and isinstance(result[k], (list, tuple)):
            return result[k]
    return None

async def test_scraper(username, max_followers=0, max_following=0):
    test_username = username

    try:
        print(f"Starting fetch for @{test_username}")
        print(f"Requesting followers: {max_followers}, following: {max_following} (tweets will be skipped)")

        # Ask the scraper to skip tweets and only fetch followers/following
        result = await scrape_twitter(
            username=test_username,
            max_tweets=0,         # do not fetch tweets
            max_retweets=0,
            max_followers=max_followers,
            max_following=max_following,
            # keep stop_date None (not used here)
        )

        print("\nFetch completed successfully!")
        # Try to find follower list in a few common key names
        followers = extract_list(result, ['followers', 'followers_list', 'followers_data', 'followers_users'])
        following = extract_list(result, ['following', 'following_list', 'friends', 'following_data', 'following_users'])

        # Print profile summary if available
        profile = result.get('user_profile') or result.get('profile') or {}
        print("Profile summary:")
        if profile:
            # print a few useful fields if present
            print("  username:", profile.get('username') or profile.get('screen_name') or test_username)
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

        # Utility to print lists with a limit
        def print_list(name, data, limit=20):
            if data is None:
                print(f"\n{name}: (not present in result)")
                return
            print(f"\n{name}: total returned = {len(data)}; showing up to {limit}:")
            for i, item in enumerate(data[:limit], start=1):
                # item might be a dict or string; try to print username if dict
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
            if len(data) > limit:
                print(f"  ... (+{len(data)-limit} more)")

        print_list("Followers", followers)
        print_list("Following", following)

        return True

    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch only followers/following for a username (no tweets).')
    parser.add_argument('username', help='Twitter username to fetch (without @)')
    parser.add_argument('--max-followers', type=int, default=100, help='Maximum number of followers to fetch (default: 100)')
    parser.add_argument('--max-following', type=int, default=100, help='Maximum number of following to fetch (default: 100)')
    parser.add_argument('--show', type=int, default=20, help='How many entries to display from each list (default: 20)')

    args = parser.parse_args()

    success = asyncio.run(test_scraper(
        username=args.username,
        max_followers=args.max_followers,
        max_following=args.max_following
    ))
    if success:
        print("\nTest passed - fetch appears to be working!")
    else:
        print("\nTest failed - please check the errors above")
        sys.exit(1)
