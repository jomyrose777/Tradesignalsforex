import time
import re
import subprocess
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import streamlit as st
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from webdriver_manager.chrome import ChromeDriverManager
import logging

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

# Step 2: Initialize the WebDriver
def initialize_webdriver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver initialized successfully.")
        return driver

    except Exception as e:
        st.error(f"Error initializing WebDriver: {e}")
        logging.error(f"WebDriver initialization failed: {e}")
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

    # Example logic to extract trading signal from the message
    if "BUY" in message_text.upper():
        execute_trade(st.session_state.driver, "BUY")
    elif "SELL" in message_text.upper():
        execute_trade(st.session_state.driver, "SELL")
    else:
        logging.warning("No valid trading signal found in the message.")

# Step 5: Execute trades on Pocket Option
def execute_trade(driver, signal):
    if not driver:
        logging.error("WebDriver is not available for trading.")
        return

    try:
        logging.info(f"Executing {signal} trade with amount: {trade_amount}")
        # Add code to execute the trade on Pocket Option
        # This might involve navigating to the trade screen and placing the trade based on the signal
        time.sleep(2)  # Simulate the time taken to place a trade
        logging.info(f"{signal} trade executed successfully.")

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
    
    st.session_state.driver = initialize_webdriver()
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
