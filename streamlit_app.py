import time
import re
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import streamlit as st
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from webdriver_manager.chrome import ChromeDriverManager

# Telegram bot configuration
telegram_token = '7501900076:AAH_te48Nyq1Oai7MHIJvgLCUAF-Y3Fr0OA'
chat_id = '@G33 NORMAL SIGNALS'

# Pocket Option credentials
pocket_option_username = 'brightai234451@gmail.com'
pocket_option_password = 'Jude@1234'

# Trade amount
trade_amount = 200  # Amount to trade

# Step 1: Get Chrome and ChromeDriver versions and ensure they match
def get_chrome_version():
    try:
        # Adjust the command based on your operating system
        chrome_version_command = "google-chrome --version" if subprocess.os.name != 'nt' else \
                                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'

        result = subprocess.run(chrome_version_command, shell=True, capture_output=True, text=True, check=True)
        version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)

        if version_match:
            return version_match.group(0)
        else:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise ValueError("Chrome version not found in output.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error checking Chrome version: {e}") from e

def get_chromedriver_version(chromedriver_path):
    try:
        chromedriver_version_command = f'"{chromedriver_path}" --version'
        result = subprocess.run(chromedriver_version_command, shell=True, capture_output=True, text=True, check=True)
        version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)

        if version_match:
            return version_match.group(0)
        else:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise ValueError("ChromeDriver version not found in output.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error checking ChromeDriver version: {e}") from e

def check_versions_match():
    try:
        chrome_version = get_chrome_version()
        # Adjust the user path
        chromedriver_path = r"C:/Users/jomyr/OneDrive/Desktop/chromedriver/chromedriver.exe"
        chromedriver_version = get_chromedriver_version(chromedriver_path)

        print(f"Chrome version: {chrome_version}")
        print(f"ChromeDriver version: {chromedriver_version}")

        if chrome_version in chromedriver_version:
            print("Chrome and ChromeDriver versions match.")
        else:
            print("Versions do not match. Please update accordingly.")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except RuntimeError as e:
        print(f"An error occurred: {e}")

# Run the version check
check_versions_match()

# Initialize Streamlit
st.title("Automated Trading Bot for Pocket Option")
st.write("Monitoring Telegram channel for signals...")

# Step 2: Initialize the WebDriver
def initialize_webdriver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(executable_path=ChromeDriverManager().install())  # Automatically manage ChromeDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error initializing WebDriver: {e}")
        return None

# Step 3: Log in to Pocket Option
def login_to_pocket_option(driver):
    if not driver:
        st.error("WebDriver not initialized. Cannot proceed with login.")
        return False

    st.write("Logging into Pocket Option...")
    driver.get("https://pocketoption.com/")

    # Log in to Pocket Option
    driver.find_element(By.ID, 'login-username').send_keys(pocket_option_username)
    driver.find_element(By.ID, 'login-password').send_keys(pocket_option_password)
    driver.find_element(By.ID, 'login-button').click()

    # Wait for the login process to complete
    time.sleep(5)

    # Navigate to the Quick Trading Demo account
    st.write("Switching to Quick Trading Demo account...")
    driver.find_element(By.XPATH, '//span[text()="Quick Trading Demo account"]').click()
    time.sleep(3)
    return True

# Step 4: Parse the signals from Telegram messages
def parse_signal(message):
    buy_signal = re.search(r'Summary:\s+BUY OPTION', message)
    sell_signal = re.search(r'Summary:\s+SELL OPTION', message)
    expiration_time = re.search(r'Expiration time:\s+(\d+)\s+MINUTES', message)
    opening_price = re.search(r'Opening price:\s+(\d+\.\d+)', message)
    
    if (buy_signal or sell_signal) and expiration_time and opening_price:
        return {
            "action": "buy" if buy_signal else "sell",
            "expiration_time": int(expiration_time.group(1)),
            "price": float(opening_price.group(1))
        }
    return None

# Step 5: Place the trade based on the parsed signals
def place_trade(driver, action, expiration_time, price):
    st.write(f"Placing a {action.upper()} trade for {expiration_time} minutes at price {price}...")

    # Interact with the Pocket Option web interface to place the trade
    if action == "buy":
        buy_button = driver.find_element(By.XPATH, '//button[contains(@class, "buy-button-selector")]')
        buy_button.click()
    elif action == "sell":
        sell_button = driver.find_element(By.XPATH, '//button[contains(@class, "sell-button-selector")]')
        sell_button.click()
    
    # Set the trade amount if necessary (this step depends on the UI)
    trade_amount_input = driver.find_element(By.XPATH, '//input[@class="trade-amount-selector"]')
    trade_amount_input.clear()
    trade_amount_input.send_keys(str(trade_amount))
    
    # Confirm the trade (if needed)
    confirm_button = driver.find_element(By.XPATH, '//button[@class="confirm-button-selector"]')
    confirm_button.click()
    
    st.write("Trade placed successfully!")

# Step 6: Handle Telegram messages
def handle_message(update: Update, context):
    message = update.message.text
    signal = parse_signal(message)
    if signal:
        driver = context.bot_data.get('driver')
        if driver:
            place_trade(driver, signal['action'], signal['expiration_time'], signal['price'])
        else:
            st.error("WebDriver not initialized. Cannot place trade.")

# Step 7: Monitor the Telegram channel for signals
def monitor_telegram_channel(driver):
    # Initialize the bot application
    application = Application.builder().token(telegram_token).build()

    # Store the driver in bot_data for use in handlers
    application.bot_data['driver'] = driver

    # Add the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    application.run_polling()

# Streamlit button to start trading
if st.button('Start Trading'):
    st.write("Bot is now running...")
    driver = initialize_webdriver()
    if login_to_pocket_option(driver):
        monitor_telegram_channel(driver)

# Clean up
if st.button('Stop Trading'):
    if 'driver' in locals():
        driver.quit()
    st.write("Trading stopped and browser closed.")
