import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.common.exceptions import TimeoutException
import pickle
from selenium.common.exceptions import NoSuchElementException

COOKIES_FILE = "cookies.pkl"

def save_cookies(driver, file_path=COOKIES_FILE):
    with open(file_path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    logging.info("Cookies saved successfully.")

def load_cookies(driver, file_path=COOKIES_FILE):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")
    else:
        logging.info("Cookies file not found.")

def is_logged_in(driver):
    try:
        driver.find_element(By.XPATH, "//div[@class='profile-rail-card']")
        return True
    except NoSuchElementException:
        return False


logging.basicConfig(filename='automation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_internet(url="https://www.google.com", timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        logging.error("No internet connection available.")
        return False

def load_messages(file_path):
    with open(file_path, 'r') as file:
        messages = file.readlines()
    return [message.strip() for message in messages]

def load_keywords(file_path):
    with open(file_path, 'r') as file:
        keywords = file.readlines()
    return [keyword.strip() for keyword in keywords]

service = FirefoxService(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)

messages = load_messages('messages.txt')

keywords = load_keywords('keywords.txt')

while not check_internet():
    time.sleep(10)

driver.get("https://www.linkedin.com/uas/login")
time.sleep(2)

if "login" in driver.current_url:
    username = driver.find_element(By.XPATH, "//input[@name='session_key']")
    password = driver.find_element(By.XPATH, "//input[@name='session_password']")
    #email
    username.send_keys("uzair_rajput@hotmail.com")
    #password
    password.send_keys("OzZi@1688")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    logging.info("Logged in successfully.")
    time.sleep(20)
    save_cookies(driver)
else:
            logging.info("Already logged in using cookies.")
try:
    for keyword in keywords:
        logging.info(f"Starting keyword: {keyword}")
        for n in range(1, 101): 
            if not check_internet():
                logging.error("Internet connection lost. Waiting for reconnection...")
                while not check_internet():
                    time.sleep(10)
                logging.info("Internet connection restored.")

            driver.get(f"https://www.linkedin.com/search/results/people/?keywords={keyword}&network=%5B%22F%22%5D&origin=FACETED_SEARCH&page={n}")
            time.sleep(5)

            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            message_buttons = [btn for btn in all_buttons if btn.text == "Message"]

            for i in range(min(len(message_buttons), 10)): 
                driver.execute_script("arguments[0].click();", message_buttons[i])
                logging.info(f"Clicked 'Message' for person {i+1} on page {n} with keyword '{keyword}'.")
                time.sleep(5)

                main_div = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'msg-form__msg-content-container')]"))
                )
                driver.execute_script("arguments[0].click();", main_div)
                time.sleep(5)

                message_area = driver.find_element(By.XPATH, "//div[@role='textbox']")
                message_area.send_keys(Keys.CONTROL + "a")
                message_area.send_keys(Keys.BACKSPACE)
                time.sleep(5)

                selected_message = random.choice(messages)

                personalized_message = f"{selected_message}"

                message_area.send_keys(personalized_message)
                logging.info(f"Typed message: {personalized_message}")
                time.sleep(5)

                send_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                driver.execute_script("arguments[0].click();", send_button)
                logging.info(f"Sent message to person {i+1} on page {n} with keyword '{keyword}'.")
                time.sleep(5)
                
                try:

                    script = """
   (function() {
        'use strict';
        // Example JavaScript code to close a message window
        function closeMessageWindow() {
            const closeButton = document.querySelector('.msg-convo-wrapper header .msg-overlay-bubble-header__controls.display-flex.align-items-center button:last-child');
            if (closeButton) {
                closeButton.click();
                console.log('Message window closed');
            } else {
                console.log('Close button not found');
            }
        }
        setTimeout(closeMessageWindow, 2000);
    })();
    """

                    driver.execute_script(script)
                    print("window close successfully.")
                except TimeoutException:
                    time.sleep(5)
except Exception as e:
        logging.error(f"Error occurred while trying to close the message window: {e}")
        time.sleep(600)
finally:
    driver.quit()
    logging.info("WebDriver session ended.")