# Ananas Discount Checker

A lightweight Python automation project that checks the active Ananas promotion page, extracts the current deal details, captures a product screenshot, and sends the result via email.

This project was built as a practical web-scraping and automation example and can be scheduled to run periodically to monitor discount campaigns.

## Features

- Headless browser automation with Selenium
- Live detection of active promotion content on the Ananas website
- Product name and price extraction from the loaded DOM
- Screenshot capture of the highlighted deal
- HTML email notification with embedded image
- Environment-based credentials for safe configuration

## Tech Stack

- Python 3
- Selenium
- BeautifulSoup
- Gmail SMTP via Python `smtplib`

## How it works

1. The script opens the Ananas promo page in a headless Chrome browser.
2. It waits for the active campaign text to appear in the page content.
3. It finds the product card associated with that promotion.
4. It extracts the product name and price values.
5. It captures a screenshot of the relevant product block.
6. It sends an HTML email containing the deal information and screenshot to a configured receiver.

## Project structure

- `ananas_scraper_selenium.py` — main scraper and email logic
- `README.md` — project documentation

## Requirements

Before running the project, install the dependencies:

```bash
pip install selenium beautifulsoup4
```

You also need:

- Python 3.9+
- Google Chrome installed on the machine
- A valid Gmail account for sending emails

## Configuration

This project reads its credentials from environment variables instead of hardcoding them into the source code.

Set the following before running the script:

```bash
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_RECEIVER="recipient@example.com"
```

Note: For Gmail, it is recommended to use an App Password instead of your main account password.

## Run the script

```bash
python ananas_scraper_selenium.py
```

If a live deal is found, the script will send an email to the configured recipient.

## Optional scheduling

This script can be scheduled to run every 2 hours using cron, systemd, or a task scheduler.

Example cron job:

```bash
0 */2 * * * /usr/bin/python3 /path/to/ananas_scraper_selenium.py >> /path/to/ananas.log 2>&1
```

## Notes

- The script is tailored to the current Ananas promotion page structure and may need adjustments if the website layout changes.
- The code intentionally uses a specific product text check for the Rođendanska campaign, so it is not a fully generalized scraper.
- For public-facing use, be careful not to expose real email credentials or secret configuration values.

## Security considerations

Before making the repository public, make sure that:

- no `.env` files are committed
- no real Gmail password or API token is stored in the repo
- any local secrets remain in environment variables only

## License

This project is currently provided for educational and personal automation use. Add a license if you plan to share it more formally with others.
