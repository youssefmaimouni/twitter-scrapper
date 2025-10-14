## Twitter Scraper

This project allows you to scrape Twitter user profiles, followers, and following lists using Playwright automation.

---

### Setup

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

### Usage

1. **Run the scraper:**
   ```bash
   python scraping_automatisation.py
   ```

2. **Output:**
   - Scraped profile data will be saved as JSON files in the `scraped_profiles` folder.
   - The script prints a summary of each profile, followers, and following in the terminal.

3. **Modify target usernames:**
   - Edit the `usernames` list in `scraping_automatisation.py` to scrape different Twitter accounts.

---

### Notes

- Make sure you have a stable internet connection.
- This tool is for educational and research purposes only. Respect Twitter's terms of service.