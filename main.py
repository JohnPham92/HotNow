from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from pytz import timezone
from sendgrid import SendGridAPIClient, To
from sendgrid.helpers.mail import Mail
from secrets import SENDGRID_API_KEY, PHONE_NUMBERS
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter, getLogger
import logging
import os

module_path = os.path.dirname(os.path.realpath(__file__))

latest_status_file = os.path.join(module_path, "status.txt")
logs_filename = os.path.join(module_path, "runtime.log")

BASE_MAIN_URL = "https://krispykreme.com/shop/order-select-store?location="
target_zip_code = "10010"
target_location_name = 'New York - Flatiron E 23rd'
visit_url = BASE_MAIN_URL + target_zip_code
CURRENT_TIMESTAMP = datetime.now(timezone("US/Eastern"))
PHONE_NUMBER_TMOB = '@tmomail.net'


def create_logger() -> object:
    """
    this creates the logger and the subsequent management
    :return:
    """
    logger = getLogger()
    handler = TimedRotatingFileHandler(
        filename=logs_filename,
        when="D",
        interval=1,
        backupCount=10,
        encoding="utf-8",
        delay=False,
    )
    formatter = Formatter(fmt=f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def create_driver_object() -> object:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    return driver


def get_page_source(driver: object, visit_url: str) -> object:
    """
    this retrieves the soup object for parsing
    :param visit_url: the url that contains the  location
    :rtype: object
    """
    driver.get(visit_url)
    wait = WebDriverWait(driver, 20)
    element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'location-card')))
    if not element:
        return
    page_source = driver.page_source
    logging.info('Successfully retrieved the page')
    driver.quit()
    return page_source


def get_locations_info(page_source: object) -> dict:
    locations_info = {}
    soup = BeautifulSoup(page_source, 'html.parser')
    for location in soup.findAll("div", attrs={"data-track": "location-search-grocery-item"}):
        location_name = location.find('h2').text
        is_hot_light_on = False
        if location.find("a", attrs={"class": "btn-hotlight on"}):
            is_hot_light_on = True
        locations_info[location_name] = is_hot_light_on
    logging.info(locations_info)
    return locations_info


def check_if_hot_light_on(locations_info: dict, target_location_name) -> bool:
    return locations_info.get(target_location_name)


def record_status(target_location_name: str, hot_light_status: bool, current_timestamp: datetime):
    f = open(latest_status_file, 'a+')
    f.write(f'{target_location_name}, {hot_light_status}, {current_timestamp}' + "\n")


def send_text(phone_numbers: list, current_timestamp: datetime, target_location_name: str):
    message = Mail(
        from_email="john@johnpham.me",
        # currently, this is configured for tmobile
        to_emails=[To(phone + PHONE_NUMBER_TMOB) for phone in phone_numbers],
        subject=f"{target_location_name} is HOT NOW! {current_timestamp}",
        is_multiple=True,
        plain_text_content=f'{current_timestamp}'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logging.info("Successful Text Sent")
    except Exception as e:
        logging.warning(e.message)


def main():
    create_logger()
    driver = create_driver_object()
    page_source = get_page_source(driver, visit_url)
    locations_info = get_locations_info(page_source)
    hot_light_status = check_if_hot_light_on(locations_info, target_location_name)
    record_status(target_location_name, hot_light_status, CURRENT_TIMESTAMP)
    if hot_light_status:
        send_text(PHONE_NUMBERS, CURRENT_TIMESTAMP, target_location_name)


if __name__ == "__main__":
    main()
