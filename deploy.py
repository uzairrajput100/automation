import streamlit as st
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

LOG_FILE = 'automation_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_internet(url="https://www.google.com", timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        logging.error("No internet connection available.")
        return False

def setup_driver():
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)
    return driver

def automate_linkedin(driver, email, password, keywords, messages):
    try:
        while not check_internet():
            time.sleep(10)

        driver.get("https://www.linkedin.com/uas/login")
        time.sleep(5)

        if "login" in driver.current_url:
            username = driver.find_element(By.XPATH, "//input[@name='session_key']")
            password_input = driver.find_element(By.XPATH, "//input[@name='session_password']")
            username.send_keys(email)
            password_input.send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            logging.info("Logged in successfully.")
            time.sleep(15)

        for keyword in keywords:
            logging.info(f"Starting keyword: {keyword}")
            for n in range(1, 101):
                if not check_internet():
                    logging.error("Internet connection lost. Waiting for reconnection...")
                    while not check_internet():
                        time.sleep(10)
                    logging.info("Internet connection restored.")

                driver.get(f"https://www.linkedin.com/search/results/people/?keywords={keyword}&network=%5B%22F%22%5D&origin=FACETED_SEARCH&page={n}")
                time.sleep(10)

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

                    message_area.send_keys(selected_message)
                    logging.info(f"Typed message: {selected_message}")
                    time.sleep(5)

                    send_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    driver.execute_script("arguments[0].click();", send_button)
                    logging.info(f"Sent message to person {i+1} on page {n} with keyword '{keyword}'.")
                    time.sleep(5)
# Close the message window
                try:
                    script = """
    (function() {
        'use strict';

        // Function to simulate click on the close button
        function closeMessageWindow() {
            // Select the button using its class name
            const button = document.querySelector('button.msg-overlay-bubble-header__button.msg-overlay-bubble-header__button--secondary');

            // Check if the button exists
            if (button) {
                // Trigger a click event on the button
                button.click();
                console.log('Close button clicked.');
            } else {
                console.log('Close button not found.');
            }
        }

        // Wait for 2 seconds and then trigger the button click
        setTimeout(closeMessageWindow, 2000);
    })();
    """
                    driver.execute_script(script)
                    logging.info("Attempted to close the message window.")
                    print("Attempted to close the message window.")
                except TimeoutException:
                    logging.error("Failed to close the message window: TimeoutException occurred.")
                    print("Window not closed due to a timeout.")
                except Exception as e:
                    logging.error(f"Failed to close the message window: {str(e)}")
                    print(f"Window not closed due to an error: {str(e)}")
                    time.sleep(2)
    #             try:
    #                 script = """
    # (function() {
    #     'use strict';

    #     // Function to simulate click on the button
    #     function triggerButtonClick() {
    #         // Select the button using its class name
    #         const button = document.querySelector('.msg-convo-wrapper header.msg-overlay-bubble-header.msg-overlay-conversation-bubble-header.justify-space-between.premium-accent-bar button:nth-child(2)');

    #         // Check if the button exists
    #         if (button) {
    #             // Trigger a click event on the button
    #             button.click();
    #             console.log('Button clicked');
    #         } else {
    #             console.log('Button not found');
    #         }
    #     }

    #     // Wait for 2 seconds and then trigger the button click
    #     setTimeout(triggerButtonClick, 2000);
    # })();
    # """
    #                 driver.execute_script(script)
    #                 logging.info("Message window closed successfully.")
    #                 print("Window closed successfully.")
    #             except TimeoutException:
    #                 logging.error("Failed to close the message window: TimeoutException occurred.")
    #                 print("Window not closed due to a timeout.")
    #             except Exception as e:
    #                 logging.error(f"Failed to close the message window: {str(e)}")
    #                 print(f"Window not closed due to an error: {str(e)}")
    #                 time.sleep(2)

    except Exception as e:
        logging.error(f"Error occurred while trying to close the message window: {e}")
        time.sleep(600)

    finally:
        driver.quit()
        logging.info("WebDriver session ended.")

st.title("LinkedIn Automation Tool")

email = st.text_input("LinkedIn Email")
password = st.text_input("LinkedIn Password", type="password")

keywords_input = st.text_area("Keywords (comma-separated)")
keywords = [keyword.strip() for keyword in keywords_input.split(",")]

messages_input = st.text_area("Messages (each message in a new line)")
messages = [message.strip() for message in messages_input.split("\n")]

if st.button("Start Automation"):
    if email and password and keywords and messages:
        st.write("Starting automation...")
        driver = setup_driver()
        automate_linkedin(driver, email, password, keywords, messages)
        st.write("Automation completed. Check the log file for details.")
        with open(LOG_FILE, "rb") as file:
            btn = st.download_button(
                label="Download Log File",
                data=file,
                file_name="automation_log.txt",
                mime="text/plain"
            )
    else:
        st.error("Please provide all required inputs.")
