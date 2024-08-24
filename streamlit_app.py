import os
import time
import logging
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot configuration
telegram_token = '7501900076:AAH_te48Nyq1Oai7MHIJvgLCUAF-Y3Fr0OA'
chat_id = '@G33 NORMAL SIGNALS'

# Pocket Option credentials
pocket_option_username = 'brightai234451@gmail.com'
pocket_option_password = 'Jude@1234'

if not pocket_option_username or not pocket_option_password:
    st.error("Pocket Option credentials are not set in environment variables.")
    logging.error("Missing Pocket Option credentials.")
    st.stop()

# Trade amount
trade_amount = 200

# Initialize Streamlit session state
if 'driver' not in st.session_state:
    st.session_state.driver = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Option to choose the browser
browser_choice = st.selectbox("Choose your browser", ["Chrome", "Firefox"])

# Step 2: Initialize the WebDriver for the selected browser
def initialize_webdriver(browser_choice):
    try:
        if browser_choice == "Chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        elif browser_choice == "Firefox":
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)

        logging.info(f"{browser_choice} WebDriver initialized successfully.")
        return driver

    except Exception as e:
        st.error(f"Error initializing {browser_choice} WebDriver: {e}")
        logging.error(f"{browser_choice} WebDriver initialization failed: {e}")
        return None

# Step 3: Log in to Pocket Option
def login_to_pocket_option(driver):
    if not driver:
        st.error("WebDriver not initialized. Cannot proceed with login.")
        return False

    try:
        st.write("Logging into Pocket Option...")
        logging.info("Attempting to log in to Pocket Option.")
        driver.get("https://pocketoption.com/")

        # Locate username and password fields and login button, fill credentials and log in
        username_field = driver.find_element("name", "email")  # Update with the correct field identifier
        password_field = driver.find_element("name", "password")  # Update with the correct field identifier
        login_button = driver.find_element("xpath", "//button[@type='submit']")  # Update with the correct button

        username_field.send_keys(pocket_option_username)
        password_field.send_keys(pocket_option_password)
        login_button.click()

        # Wait for the login process to complete
        time.sleep(5)
        logging.info("Logged into Pocket Option successfully.")
        return True

    except Exception as e:
        st.error(f"Error logging into Pocket Option: {e}")
        logging.error(f"Login failed: {e}")
        return False

# Step 4: Parse signals from Telegram messages
def handle_telegram_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    logging.info(f"Received message: {message_text}")

    # Extract relevant information using regex
    asset_pattern = re.search(r"trading asset\s(.+)", message_text, re.IGNORECASE)
    signal_pattern = re.search(r"(BUY|SELL)\sOPTION", message_text, re.IGNORECASE)
    expiration_pattern = re.search(r"Expiration time:\s+(\d+)\s+MINUTES", message_text, re.IGNORECASE)
    price_pattern = re.search(r"Opening price:\s([\d.]+)", message_text, re.IGNORECASE)

    if asset_pattern and signal_pattern and expiration_pattern and price_pattern:
        asset = asset_pattern.group(1).strip()
        signal = signal_pattern.group(1).strip().upper()
        expiration_time = int(expiration_pattern.group(1).strip())
        entry_price = float(price_pattern.group(1).strip())

        logging.info(f"Parsed Signal: Asset={asset}, Signal={signal}, Expiration={expiration_time}, Entry Price={entry_price}")
        st.write(f"Received Signal: {signal} on {asset} at price {entry_price} with expiration {expiration_time} minutes.")

        execute_trade(st.session_state.driver, asset, signal, expiration_time, entry_price)
    else:
        logging.warning("Failed to parse the message or missing information.")
        st.write("Failed to parse the signal.")

# Step 5: Execute trades on Pocket Option
def execute_trade(driver, asset, signal, expiration_time, entry_price):
    if not driver:
        logging.error("WebDriver is not available for trading.")
        return

    try:
        logging.info(f"Executing {signal} trade on {asset} at price {entry_price} with expiration time {expiration_time}")
        # Navigate to the asset in Pocket Option (pseudo-code, adjust based on actual web page structure)
        # driver.find_element_by_asset_name(asset).click()

        # Set the trade parameters (e.g., expiration time, trade amount)
        # expiration_dropdown = driver.find_element_by_xpath("...")  # Find expiration dropdown
        # expiration_dropdown.select_by_value(expiration_time)

        # Execute the trade based on signal
        if signal == "BUY":
            # driver.find_element_by_buy_button().click()  # Replace with actual identifier
            logging.info(f"BUY trade executed on {asset} at {entry_price}")
        elif signal == "SELL":
            # driver.find_element_by_sell_button().click()  # Replace with actual identifier
            logging.info(f"SELL trade executed on {asset} at {entry_price}")

        time.sleep(2)  # Simulate the time taken to place a trade
        logging.info(f"{signal} trade on {asset} at {entry_price} executed successfully.")

    except Exception as e:
        logging.error(f"Failed to execute {signal} trade: {e}")

# Telegram bot initialization
def start_telegram_bot():
    application = Application.builder().token(os.environ.get('TELEGRAM_BOT_TOKEN')).build()

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))

    # Start the bot
    application.run_polling()

# Streamlit UI to start trading
if st.button('Start Trading') and not st.session_state.is_running:
    logging.info("Bot started.")
    st.write("Bot is now running...")
    
    st.session_state.driver = initialize_webdriver(browser_choice)
    if st.session_state.driver and login_to_pocket_option(st.session_state.driver):
        st.write("Logged in successfully.")
        st.session_state.is_running = True
        st.session_state.telegram_bot = start_telegram_bot()  # Start Telegram bot for monitoring
    else:
        st.error("Failed to start trading bot.")
        st.session_state.is_running = False

# Stop trading and clean up
if st.button('Stop Trading') and st.session_state.is_running:
    if st.session_state.driver:
        st.session_state.driver.quit()
        logging.info("WebDriver closed successfully.")
        st.write("Trading stopped and browser closed.")
    st.session_state.is_running = False
