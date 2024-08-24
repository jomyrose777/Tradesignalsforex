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

# Step 2: Initialize the WebDriver
def initialize_webdriver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: Run Chrome in headless mode
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
        
        # Log in to Pocket Option
        driver.find_element(By.ID, 'login-username').send_keys(pocket_option_username)
        driver.find_element(By.ID, 'login-password').send_keys(pocket_option_password)
        driver.find_element(By.ID, 'login-button').click()

        # Wait for the login process to complete
        time.sleep(5)
        logging.info("Logged into Pocket Option successfully.")
        return True
    
    except Exception as e:
        st.error(f"Error logging into Pocket Option: {e}")
        logging.error(f"Login failed: {e}")
        return False

# Step 4: Parse the signals from Telegram messages
def parse_signal(message):
    try:
        buy_signal = re.search(r'Your Trading Strategy: BUY', message)
        sell_signal = re.search(r'Your Trading Strategy: SELL', message)
        expiration_time = re.search(r'Expiration time:\s+(\d+)\s+MINUTES', message)
        opening_price = re.search(r'Opening price:\s+(\d+\.\d+)', message)
        
        if (buy_signal or sell_signal) and expiration_time and opening_price:
            logging.info(f"Signal parsed: Action - {'buy' if buy_signal else 'sell'}, Expiration - {expiration_time.group(1)}, Price - {opening_price.group(1)}")
            return {
                "action": "buy" if buy_signal else "sell",
                "expiration_time": int(expiration_time.group(1)),
                "price": float(opening_price.group(1))
            }
        else:
            logging.warning("Signal parsing failed. Incomplete or invalid signal.")
            return None
    except Exception as e:
        logging.error(f"Error parsing signal: {e}")
        return None

# Streamlit UI to start trading
if st.button('Start Trading'):
    logging.info("Bot started.")
    st.write("Bot is now running...")
    driver = initialize_webdriver()
    if driver and login_to_pocket_option(driver):
        st.write("Logged in successfully.")
        # Start monitoring the Telegram channel
        # monitor_telegram_channel(driver)  # Uncomment and implement this function based on your needs
    else:
        st.error("Failed to start trading bot.")

# Clean up
if st.button('Stop Trading'):
    if 'driver' in locals():
        driver.quit()
        logging.info("WebDriver closed successfully.")
    st.write("Trading stopped and browser closed.")
