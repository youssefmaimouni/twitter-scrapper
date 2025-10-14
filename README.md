# Twitter Scraper

This project allows you to scrape Twitter user profiles, tweets, followers, and following lists using **Playwright automation**.

---

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
playwright install
```

2. **(Optional) Configure Playwright Browsers:**

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

### 3️⃣ Run the scraper

1. Open `scraping_automatisation.py` and modify the `usernames` list with the Twitter accounts you want to scrape:

```python
usernames = ["elonmusk", "Cr7Fran4ever"]
```

2. Run the scraper:

```bash
python scraping_automatisation.py
```

3. Output:

* Scraped profile data will be saved as JSON files in the `scraped_profiles/` folder.
* The terminal will display a summary of each profile, followers, and following.

---

## Notes

* Make sure you have a stable internet connection.
* This tool is for **educational and research purposes only**. Respect Twitter's terms of service.
* Always ensure cookies are **up-to-date** to avoid login errors.
* If the scraper encounters `sameSite` errors, run `fix_cookies.py` before rerunning the scraper.

---
