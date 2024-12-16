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
