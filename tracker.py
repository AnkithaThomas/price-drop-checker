import re
import requests
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_PASSWORD")

def extract_asin(url_or_asin):
    if re.fullmatch(r"[A-Z0-9]{10}", url_or_asin):
        return url_or_asin
    try:
        response = requests.get(url_or_asin, allow_redirects=True, timeout=10)
        final_url = response.url

        match = re.search(r"/dp/([A-Z0-9]{10})", final_url)
        if match:
            return match.group(1)

    except requests.RequestException:
        pass

    return None

def get_price(asin):
    """Get the current price of a product using SerpApi"""
    url = "https://serpapi.com/search"
    params = {
        "engine" : "amazon_product",
        "api_key" : SERPAPI_KEY,
        "asin" : asin
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)  # optional, just to debug once

        product = data.get("product_results", {})

        if "extracted_price" in product:
            return float(product["extracted_price"])

        if "price" in product:
            price_str = product["price"].replace("$", "").replace(",", "")
            return float(price_str)

        print("Could not find price in API response:", product)
        return None

    except (KeyError, IndexError, TypeError):
        print("Could not find price in API response")
        return None
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def send_email(to_email, price, url):
    """Send email alert if price drops"""
    msg = EmailMessage()
    msg["Subject"] = "Price Drop Alert!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"The price dropped to ${price} for {url}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_price(url_or_asin, target_price, email):
    """Check price and return a message for display"""
    asin = extract_asin(url_or_asin)
    if not asin:
        return "Could not extract ASIN from URL"

    current_price = get_price(asin)
    if current_price is None:
        return "Price is not available"

    if current_price <= target_price:
        send_email(email, current_price, url_or_asin)
        return f"Current price ${current_price} is below your target ${target_price}. Email sent!"
    else:
        return f"Current price ${current_price} is still above your target ${target_price}."
