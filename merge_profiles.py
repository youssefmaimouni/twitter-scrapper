import json
import os

# Load twitter_location_only.json
with open("twitter_location_only.json", "r", encoding="utf-8") as f:
    location_data = json.load(f)

# Load profile_images_links.json
with open("profile_images_links.json", "r", encoding="utf-8") as f:
    images_data = json.load(f)

# Create a dict for fast lookup of image_url
images_dict = {entry["username"]: entry["image_url"] for entry in images_data if "username" in entry}

# Directory containing scraped profiles
profiles_dir = "scraped_profiles"

for entry in location_data:
    username = entry.get("Twitter Username")
    if username:
        # Add image_url if available
        entry["image_url"] = images_dict.get(username)
        # Add profile data if available
        profile_path = os.path.join(profiles_dir, f"{username}.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as pf:
                try:
                    profile_data = json.load(pf)
                    entry["profile_data"] = profile_data
                except Exception as e:
                    entry["profile_data"] = None
        else:
            entry["profile_data"] = None


# Save the merged result
with open("twitter_location_only_completed.json", "w", encoding="utf-8") as f:
    json.dump(location_data, f, ensure_ascii=False, indent=2)

print("Merged file saved as twitter_location_only_completed.json")