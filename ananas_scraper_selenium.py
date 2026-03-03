import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def get_deal():
    url = "https://ananas.rs/promo/rodjendananas-popust"

    # Set up "Headless" mode (so no window actually pops up)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # This helps ensure the screenshot looks sharp
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        print(f"Page title is {driver.title}")

        # Wait up to 15 seconds for page to load and for the "Rođendanska" text to appear in the DOM
        wait = WebDriverWait(driver, 15)
        string_xpath_selector = "//*[contains(normalize-space(.), 'Rođendanska cena važi još')]/ancestor::a"
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, string_xpath_selector)))
        except TimeoutException:
            print("Timeout reached: No active deals right now.")
            return None

        # Scrolling to the element so lazy-loaded images trigger
        product_element = driver.find_element(By.XPATH, string_xpath_selector)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product_element)
        # Stabilizing after scrolling
        time.sleep(1)
        # Taking screenshot of the product
        image_bytes = product_element.screenshot_as_png
        print("Screenshot of the product captured.")

        # After the page is loaded, we grab the fully rendered HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Finding all elements that contain text for the current deal:
        all_matches = soup.find_all(lambda tag: tag.name == "div" and
                                                "Rođendanska cena važi još" in tag.get_text(strip=True))
        # If the text is found among elements only the last one is picked, since all its parents contain that text
        if all_matches:
            active_badge = all_matches[-1]

            print(f"Found specific badge tag: <{active_badge.name}> with text: {active_badge.get_text(strip=True)}")
            #Finding the parent of the element that also contains children with name and price information
            product_card = active_badge.find_parent('a')

            if product_card:
                print("Parent card is found.")

                # Getting the product's name
                product_name = product_card.find('h3').get_text(strip=True)
                # Getting the product prices
                element_prices = product_card.find_all('span', class_=lambda x: x and ('iWtCrL' in x or 'JsmBJ' in x))
                product_prices = [p.get_text(strip=True) for p in element_prices]

                #Printing results for local testing
                print(f"Name: {product_name}")
                print(f"Prices: {' -> '.join(product_prices)} RSD")

                return {
                    "name": product_name,
                    "prices": product_prices,
                    "image": image_bytes
                }
            else:
                print("Parent card is not found.")
        else:
            return None


    finally:
        driver.quit()  # Always close the browser

def send_deal_mail(deal_info, sender_email,sender_password, receiver_email):
    # Creating a container using related for embedded images
    msg = MIMEMultipart('related')
    msg['Subject'] = f"Ananas Deal: {deal_info['name']}"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    #Creating the body of the e-mail
    prices_html = " -> ".join([f"<s>{p}</s>" if i < len(deal_info['prices'])-1 else f"<b>{p}</b>"
                               for i, p in enumerate(deal_info['prices'])])
    # Generating body of the mail
    html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px;">
              <h2 style="color: #FE5000;">Novi Rođendananas Popust!</h2>
              <p>Pronašli smo aktivnu ponudu za vas:</p>
              <hr>
              <h3>{deal_info['name']}</h3>
              <p style="font-size: 18px;">Cena: {prices_html} RSD</p>

              <div style="margin-top: 20px; text-align: center;">
                <img src="cid:deal_screenshot" style="max-width: 100%; height: auto; border-radius: 8px;">
              </div>

              <p style="margin-top: 20px;">
                <a href="https://ananas.rs/promo/rodjendananas-popust" 
                   style="background-color: #FE5000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Pogledaj na sajtu
                </a>
              </p>
            </div>
          </body>
        </html>
        """
    msg.attach(MIMEText(html, 'html'))
    # Attaching the screenshot part
    img = MIMEImage(deal_info['image'])
    img.add_header('Content-ID', '<deal_screenshot>')
    msg.attach(img)

    #Sending the mail with all information
    try:
        # Use Port 587 with STARTTLS instead of 465 SSL
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1) # This will print the full conversation with Google in your logs
        server.starttls() # Secure the connection
        server.login(sender_email.strip(), sender_password.strip())
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    print("Scraping with Selenium started...")
    deal = get_deal()
    if deal:
        MY_EMAIL = os.environ.get("EMAIL_SENDER")
        MY_PASSWORD = os.environ.get("EMAIL_PASSWORD")
        RECIPIENT = os.environ.get("EMAIL_RECEIVER")

        # ADDING TEMPORARY DEBUG LINE
        if not MY_EMAIL or not MY_PASSWORD:
            print(f"CRITICAL ERROR: Secrets not loaded! Email: {bool(MY_EMAIL)}, Pwd: {bool(MY_PASSWORD)}")
        else:
            # Print the length to see if there are extra characters
            print(f"DEBUG: Email length: {len(MY_EMAIL)}, Pwd length: {len(MY_PASSWORD)}")

        send_deal_mail(deal, MY_EMAIL, MY_PASSWORD, RECIPIENT)
    else:
        print("No active deal found at this moment.")
