"""
Taco Bell Account Automation Script
===================================

Author: Krish Shah
Created on: 12/15/2024

Description:
-------------
This script automates the process of creating Taco Bell accounts using email permutations. 
It performs the following tasks sequentially:
1. Dynamically generates the next permutation of a provided base email (e.g., inserting dots in usernames).
2. Automates the Taco Bell account creation process using Playwright.
3. Fetches the verification email using IMAP.
4. Completes the email verification process.

Usage:
------
1. Install the required dependencies:
   - Install Python 3.9 or higher.
   - Run `pip install playwright`.
   - Run `pip install imapclient`.
   - Run `pip install python-dotenv`.
   - Set up Playwright browsers: `playwright install`.

2. Prepare Gmail credentials:
   - Enable IMAP on your Gmail account.
   - Generate an app password for Gmail: https://myaccount.google.com/security

3. Run the script:
   python script.py
"""

import json
import os
import imaplib
import email
from email.header import decode_header
import re
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

# File to store email permutations and tracking
PERMUTATIONS_FILE = "email_permutations.json"
# File to log used email permutations dynamically
USED_EMAILS_FILE = "used_emails.txt"

def send_sms_via_email(phone_number, carrier_gateway, message, gmail_username, gmail_app_password):
    """Sends an SMS to the phone number via the carrier's email-to-SMS gateway."""
    sms_email = f"{phone_number}@{carrier_gateway}"
    try:
        # Set up the email message
        msg = MIMEText(message)
        msg["From"] = gmail_username
        msg["To"] = sms_email
        msg["Subject"] = "Taco Bell Automation Notification"

        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_username, gmail_app_password)
            server.sendmail(gmail_username, sms_email, msg.as_string())

        print(f"SMS sent to {phone_number} via {carrier_gateway}.")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

# Load or initialize the email tracking file
def load_permutations(email):
    if not os.path.exists(PERMUTATIONS_FILE):
        return {"base_email": email, "current_index": 0}
    with open(PERMUTATIONS_FILE, "r") as f:
        data = json.load(f)
        if data.get("base_email") != email:
            # Reset if the base email changes
            return {"base_email": email, "current_index": 0}
        return data

# Save the updated state
def save_permutations(data):
    with open(PERMUTATIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Append the generated email to a text file
def log_email_to_file(generated_email):
    with open(USED_EMAILS_FILE, "a") as f:
        f.write(generated_email + "\n")

# Efficiently generate the nth permutation
def generate_nth_permutation(base_email, n):
    username, domain = base_email.split("@")
    parts = list(username)
    length = len(parts)
    total_permutations = 1 << (length - 1)  # 2^(length-1)

    if n >= total_permutations:
        return None

    result = []
    for i in range(length):
        result.append(parts[i])
        if n & (1 << i):  # Add a dot if the bit is set
            result.append(".")
    return f"{''.join(result)}@{domain}"

# Step 1: Create Taco Bell Account
def create_taco_bell_account(email):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        context = browser.new_context()  # Create a new incognito-like context
        page = context.new_page()

        page.goto("https://www.tacobell.com/register/yum")
        page.fill('[name="email"]', email)
        page.click('button:has-text("Confirm")')

        try:
            page.wait_for_timeout(5000)
            print(f"Account creation attempted for {email}.")
        except Exception as e:
            print(f"Error during account creation: {e}")

        browser.close()

# Step 2: Fetch Email Verification Link
def fetch_verification_link(gmail_username, gmail_app_password, taco_email):
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(gmail_username, gmail_app_password)
        imap.select("inbox")

        search_criteria = f'TO "{taco_email}"'
        status, messages = imap.search(None, search_criteria)
        email_ids = messages[0].split()
        if not email_ids:
            print(f"No emails found for {taco_email}.")
            return None

        latest_email_id = email_ids[-1]
        status, msg_data = imap.fetch(latest_email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = None
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                if body:
                    match = re.search(r"Verify Email\s*\(\s*(https://[^\s]+)\s*\)", body)
                    if match:
                        return match.group(1)

        print("No 'Verify Email' link found.")
        return None

    except Exception as e:
        print(f"Error fetching email: {e}")
        return None

# Step 3: Complete Verification Form
def complete_verification_form(verification_link, first_name, last_name):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()  # Create a new incognito-like context
            page = context.new_page()

            page.goto(verification_link)
            page.fill('[name="first_name"]', first_name)
            page.fill('[name="last_name"]', last_name)
            page.check('[id="agreement"]')
            page.click('button:has-text("Confirm")')

            page.wait_for_timeout(5000)
            print("Verification form completed successfully.")
            browser.close()

    except Exception as e:
        print(f"Error completing verification form: {e}")

# Main Function
def main():
    # Gmail credentials
    gmail_username = os.getenv("GMAIL_EMAIL")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")  # App password

    # Base email input
    base_email = os.getenv("GMAIL_EMAIL")
    first_name = os.getenv("FIRST_NAME")  # First name for verification form
    last_name = os.getenv("LAST_NAME")  # Last name for verification form

    # Phone number and carrier gateway
    phone_number = os.getenv("PHONE_NUMBER")  # e.g., "1234567890"
    carrier_gateway = os.getenv("CARRIER_GATEWAY")  # e.g., "vtext.com" for Verizon

    # Load or initialize permutations
    data = load_permutations(base_email)

    # Generate the next email permutation
    next_permutation = generate_nth_permutation(data["base_email"], data["current_index"])
    if not next_permutation:
        print("No more permutations available.")
        return

    print(f"Next permutation: {next_permutation}")

    # Log the current permutation to the text file
    log_email_to_file(next_permutation)

    # Step 1: Create Taco Bell account
    create_taco_bell_account(next_permutation)

    # Step 2: Fetch the verification link
    verification_link = fetch_verification_link(gmail_username, gmail_app_password, next_permutation)
    if verification_link:
        # Step 3: Complete verification
        complete_verification_form(verification_link, first_name, last_name)

        # Send an SMS notification
        message = f"New Taco Bell account created successfully: {next_permutation}"
        send_sms_via_email(phone_number, carrier_gateway, message, gmail_username, gmail_app_password)

    else:
        print(f"Failed to retrieve a verification link for {next_permutation}.")

    # Increment the index and save the updated state
    data["current_index"] += 1
    save_permutations(data)

    print("Script completed successfully.")

if __name__ == "__main__":
    main()
