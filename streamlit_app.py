import time
import re
import requests
from selenium import webdriver
driver = webdriver.Chrome(executable_path='C:/Users/jomyr/OneDrive/Desktop/chromedriver')
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import streamlit as st
import telegram
from telegram.ext import Updater, MessageHandler, Filters

# Telegram bot configuration
telegram_token = '7501900076:AAH_te48Nyq1Oai7MHIJvgLCUAF-Y3Fr0OA'
chat_id = '@G33 NORMAL SIGNALS'

# Pocket Option credentials
pocket_option_username = 'brightai234451@gmail.com'
pocket_option_password = 'Jude@1234'

# Initialize Streamlit
st.title("Automated Trading Bot for Pocket Option")
st.write("Monitoring Telegram channel for signals...")

# Step 1: Initialize the WebDriver
driver = webdriver.Chrome()

def login_to_pocket_option():
    st.write("Logging into Pocket Option...")
    driver.get("https://pocketoption.com/en/login")

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

def parse_signal(message):
    buy_signal = re.search(r'Summary:\s+BUY OPTION', message)
    sell_signal = re.search(r'Summary:\s+SELL OPTION', message)
    expiration_time = re.search(r'Expiration time:\s+(\d+)\s+MINUTES', message)
    opening_price = re.search(r'Opening price:\s+(\d+\.\d+)', message)
    
    if buy_signal and expiration_time and opening_price:
        return {
            "action": "buy",
            "expiration_time": int(expiration_time.group(1)),
            "price": float(opening_price.group(1))
        }
    elif sell_signal and expiration_time and opening_price:
        return {
            "action": "sell",
            "expiration_time": int(expiration_time.group(1)),
            "price": float(opening_price.group(1))
        }
    return None

def place_trade(action, expiration_time, price):
    st.write(f"Placing a {action.upper()} trade for {expiration_time} minutes at price {price}...")
    
    # Interact with the Pocket Option web interface to place the trade
    if action == "buy":
        buy_button = driver.find_element(By.XPATH, '//button[contains(@class, "buy-button-selector")]')
        buy_button.click()
    elif action == "sell":
        sell_button = driver.find_element(By.XPATH, '//button[contains(@class, "sell-button-selector")]')
        sell_button.click()
    
    # Additional steps for setting expiration time, etc. might be needed here.
    
    st.write("Trade placed successfully!")

def handle_message(update, context):
    message = update.message.text
    signal = parse_signal(message)
    if signal:
        place_trade(signal['action'], signal['expiration_time'], signal['price'])

def monitor_telegram_channel():
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()

# Streamlit button to start trading
if st.button('Start Trading'):
    st.write("Bot is now running...")
    login_to_pocket_option()
    monitor_telegram_channel()

# Clean up
if st.button('Stop Trading'):
    driver.quit()
    st.write("Trading stopped and browser closed.")
