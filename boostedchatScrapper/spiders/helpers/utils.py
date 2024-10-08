import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_page_url_status_code(url, driver):
    page_url_status_code = 500

    # Access requests via the `requests` attribute
    for request in driver.requests:

        if request.response:
            #show all urls that are requested per page load
            print(
                request.url,
                request.response.status_code,
                request.response.headers['Content-Type']
            )


        if request.url == url:
            page_url_status_code = request.response.status_code

    return page_url_status_code


def interceptor(request):
    # stopping images from being requested
    # in case any are not blocked by imagesEnabled=false in the webdriver options above 
    if request.path.endswith(('.png', '.jpg', '.gif')):
        request.abort()

    # stopping css from being requested
    if request.path.endswith(('.css')):
        request.abort()

    # stopping fonts from being requested
    if 'fonts.' in request.path: #eg fonts.googleapis.com or fonts.gstatic.com
        request.abort()




def setup_driver(driver_version='121.0.6167.184'):


    # SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')

    # ## Define ScrapeOps Proxy Port Endpoint
    # proxy_options = {
    #     'proxy': {
    #         'http': f'http://scrapeops.headless_browser_mode=false:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
    #         'https': f'http://scrapeops.headless_browser_mode=false:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
    #         'no_proxy': 'localhost:127.0.0.1'
    #     }
    # }

    
    # options = webdriver.ChromeOptions()
    option = webdriver.ChromeOptions()
    option.add_argument('--headless') ## --> comment out to see the browser launch.
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-sh-usage')
    option.add_argument('--blink-settings=imagesEnabled=false')

    
    try:
        driver = webdriver.Chrome(options=option
                # seleniumwire_options=proxy_options
                )
    except Exception as err:
        print("your chrome version is not supported by the way")
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(
            latest_release_url='https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json',
            driver_version=driver_version).install()), options=option)
            print(f"successfully bumped up the version to {driver_version}")
        except Exception as err:
            print(err)
    return driver

def click_element(xpath):
    driver = setup_driver()
    try:
        element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))  
        element.click()
    except NoSuchElementException as err:
        logging.warning(err)
    return driver

def generate_html(url):
    driver = setup_driver()
    driver.get(url)
    return driver
