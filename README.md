# Twitter Scraper

This project allows you to scrape Twitter user profiles, tweets, followers, and following lists using **Playwright automation**.

---

## Initial Setup

1. **Create and activate virtual environment:**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
playwright install
```

3. **(Optional) Configure Playwright Browsers:**

If you encounter browser errors, run:

```bash
playwright install chromium
```

---

## Workflow

### 1️⃣ Get Twitter cookies manually

1. Open your browser and log in to Twitter.
2. Export your cookies using your browser’s developer tools or an extension (e.g., **Cookie Editor**).
3. Save the exported JSON file as:

```
app/twitter_cookies.json
```

> Ensure the JSON contains the required fields: `name`, `value`, `domain`, `path`, `expires`, and optionally `sameSite`.

---

### 2️⃣ Fix cookies (if needed)

Some cookies may cause errors (like `sameSite`) when loaded by Playwright. To fix them, run:

```bash
python fix_cookies.py
```

This script will automatically update all `sameSite` fields in `app/twitter_cookies.json` to compatible values (`Strict`, `Lax`, or `None`).

---

### 3️⃣ Run the scrapers

1. **Set up Serper API Key:**
   - Go to [https://serper.dev/](https://serper.dev/)
   - Sign up and get your API key
   - Create or edit the `.env` file in the project root
   - Add your API key:
   ```
   serper_api_key=your_api_key_here
   ```

2. First, collect Twitter usernames by running:
```bash
python get_users.py
```
This will create a `users_extended.json` file containing Twitter profiles to scrape.
his will create a `users_extended.json` file containing Twitter profiles to scrape.

3. Then, scrape the profiles by running:
```bash
python fetch_user.py
```

4. Output:
* Scraped profile data will be saved as JSON files in the `scraped_profiles/` folder.
* The terminal will display a summary of each profile, followers, and following.

---

## Notes

* Make sure you have a stable internet connection.
* This tool is for **educational and research purposes only**. Respect Twitter's terms of service.
* Always ensure cookies are **up-to-date** to avoid login errors.
* If the scraper encounters `sameSite` errors, run `fix_cookies.py` before rerunning the scraper.

---
