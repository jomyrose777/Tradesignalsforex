import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import streamlit as st
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# Telegram bot configuration
telegram_token = '7501900076:AAH_te48Nyq1Oai7MHIJvgLCUAF-Y3Fr0OA'
chat_id = '@G33 NORMAL SIGNALS'

# Pocket Option credentials
pocket_option_username = 'brightai234451@gmail.com'
pocket_option_password = 'Jude@1234'

# Trade amount
TRADE_AMOUNT = 200  # Amount to trade in dollars

# Initialize Streamlit
st.title("Automated Trading Bot for Pocket Option")
st.write("Monitoring Telegram channel for signals...")

def initialize_webdriver():
    try:
        driver = webdriver.Chrome()  # Uses default path if chromedriver is in PATH
        return driver
    except Exception as e:
        st.error(f"Error initializing WebDriver: {e}")
        return None

# Initialize WebDriver
driver = initialize_webdriver()

def login_to_pocket_option():
    if driver is None:
        st.error("WebDriver not initialized. Cannot proceed with login.")
        return
    
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

def parse_signal(message):
    buy_signal = re.search(r'Summary:\s+BUY OPTION', message)
    sell_signal = re.search(r'Summary:\s+SELL OPTION', message)
    expiration_time = re.search(r'Expiration time:\s+(\d+)\s+MINUTES', message)
    
    if buy_signal and expiration_time:
        return {
            "action": "buy",
            "expiration_time": int(expiration_time.group(1)),
            "amount": TRADE_AMOUNT
        }
    elif sell_signal and expiration_time:
        return {
            "action": "sell",
            "expiration_time": int(expiration_time.group(1)),
            "amount": TRADE_AMOUNT
        }
    return None

def place_trade(action, expiration_time, amount):
    if driver is None:
        st.error("WebDriver not initialized. Cannot place trade.")
        return
    
    st.write(f"Placing a {action.upper()} trade for ${amount} with expiration time {expiration_time} minutes...")
    
    # Interact with the Pocket Option web interface to place the trade
    if action == "buy":
        # Locate and click the buy button
        buy_button = driver.find_element(By.XPATH, '//button[contains(@class, "buy-button-selector")]')
        buy_button.click()
        # Set the trade amount
        amount_input = driver.find_element(By.XPATH, '//input[contains(@class, "amount-input-selector")]')
        amount_input.clear()
        amount_input.send_keys(str(amount))
        # Set the expiration time if necessary
        expiration_input = driver.find_element(By.XPATH, '//input[contains(@class, "expiration-input-selector")]')
        expiration_input.clear()
        expiration_input.send_keys(str(expiration_time))
        # Confirm trade
        confirm_button = driver.find_element(By.XPATH, '//button[contains(@class, "confirm-button-selector")]')
        confirm_button.click()
    elif action == "sell":
        # Locate and click the sell button
        sell_button = driver.find_element(By.XPATH, '//button[contains(@class, "sell-button-selector")]')
        sell_button.click()
        # Set the trade amount
        amount_input = driver.find_element(By.XPATH, '//input[contains(@class, "amount-input-selector")]')
        amount_input.clear()
        amount_input.send_keys(str(amount))
        # Set the expiration time if necessary
        expiration_input = driver.find_element(By.XPATH, '//input[contains(@class, "expiration-input-selector")]')
        expiration_input.clear()
        expiration_input.send_keys(str(expiration_time))
        # Confirm trade
        confirm_button = driver.find_element(By.XPATH, '//button[contains(@class, "confirm-button-selector")]')
        confirm_button.click()
    
    st.write("Trade placed successfully!")

def handle_message(update, context):
    message = update.message.text
    signal = parse_signal(message)
    if signal:
        place_trade(signal['action'], signal['expiration_time'], signal['amount'])

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
    if driver:
        driver.quit()
    st.write("Trading stopped and browser closed.")
