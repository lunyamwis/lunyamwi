import time
import re
import math
import time
import logging
import os
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from boostedchatScrapper.models import ScrappedData

CLEAN_STRING = re.compile(r"[\']")

class StyleseatScraper:
    def __init__(self, region, category):
        self.region = region
        self.category = category
        self.driver_version='121.0.6167.184'
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') ## --> comment out to see the browser launch.
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-sh-usage')
        options.add_argument('--blink-settings=imagesEnabled=false')

        
        try:
            driver = webdriver.Chrome(options=options
                    # seleniumwire_options=proxy_options
                    )
        except Exception as err:
            print("your chrome version is not supported by the way")
            try:
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(
                latest_release_url='https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json',
                driver_version=self.driver_version).install()), options=options)
                print(f"successfully bumped up the version to {self.driver_version}")
            except Exception as err:
                print(err)
        return driver

    def get_page_url_status_code(self, url, driver):
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


    def interceptor(self, request):
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






    def click_element(self, xpath):
        driver = self.driver
        try:
            element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, xpath)))  
            element.click()
        except NoSuchElementException as err:
            logging.warning(err)
        return driver

    def generate_html(self,url):
        driver = self.driver
        driver.get(url)
        return driver
    
    def generate_styleseat_links(self, url):
        driver = self.driver
        driver.get(url)
        driver.implicitly_wait(5)
        time.sleep(10)  # Wait for the page to load dynamically
        url_list = []

        list_of_seats = None
        try:
            list_of_seats = driver.find_element(By.XPATH, "//div[contains(@class,'search-results-list-component')]")
        except TimeoutException:
            print("No popup...")

        i = 0
        while True:

            try:
                loadMoreButton = list_of_seats.find_element(
                    By.XPATH, "//li[contains(@class,'load-more-wrapper')]/button"
                )
                time.sleep(4)
                logging.warning(f"state -- {i+1}")
                loadMoreButton.click()
                time.sleep(4)

            except Exception as e:
                print(e)
                break

        try:
            names = list_of_seats.find_elements(By.TAG_NAME, "h3")
        except NoSuchElementException:
            print("escape")
        for name in names:
            logging.warning(f"state --- {name}")
            name.click()
            time.sleep(5)

        for window in range(1, len(driver.window_handles)):
            try:
                driver.switch_to.window(driver.window_handles[window])
            except IndexError as err:
                print(f"{err}")

            url_list.append(driver.current_url)
            logging.warning(f"state --- {driver.current_url}")
            if window == 1:

                break
            
        driver.switch_to.window(driver.window_handles[0])
        driver.quit()

        return url_list
    
    def generate_html(self, url):
        self.driver.get(url)
        time.sleep(5)  # Wait for the page to load
        return self.driver

    def start_requests(self):
        urls = self.generate_styleseat_links(f"https://www.styleseat.com/m/search/{self.region}/{self.category}")
        for url in urls:
            page = self.generate_html(url)
            print("==================☁️☁️generated_url☁️☁️===========")
            print(page.current_url)
            print("==================☁️☁️generated_url☁️☁️===========")
            self.parse(page)

    def parse(self, page):
        styleseat_item = {}
        resp_meta = {}
        print("==================☁️☁️meta_driver☁️☁️===========")
        print(page.current_url)
        print("==================☁️☁️meta_driver☁️☁️===========")
        time.sleep(10)
        styleseat_item["name"] = "styleseat"
        styleseat_item["inference_key"] = self.region
        resp_meta["name"] = "styleseat"
        resp_meta["secondary_name"] = page.find_element(By.XPATH, '//h1[@data-testid="proName"]').text
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta["logo_url"] = page.find_element(By.XPATH, '//div[contains(@class,"avatar-icon")]').get_attribute("style")
        resp_meta["profileUrl"] = page.current_url
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta["category"] = page.find_element(By.XPATH, '//div[@data-testid="proProfession"]').text
        try:
            resp_meta["igname"] = page.find_element(By.XPATH, '///div[@data-testid="instagram-link"]/div[2]').text
        except Exception as error:
            print(error)
        resp_meta["businessName"] = page.find_element(By.XPATH, '//div[@data-testid="proBusinessName"]').text
        resp_meta["ratings"] = page.find_element(By.XPATH, '//div[@data-testid="rating-stars"]').text
        # //div[@data-testid="service-card"]
        time.sleep(7)
        services = []
        for i, elem in enumerate(page.find_elements(By.XPATH, '//div[@data-testid="service-card"]')):
            if i < 3:
                try:
                    service = {
                        "serviceTitle": page.find_elements(By.XPATH, '//h4[@data-testid="serviceTitle"]')[i].text,
                        "serviceDetails": page.find_elements(By.XPATH, '//div[@data-testid="serviceDetails"]')[i].text,
                        "descriptionSection": page.find_elements(By.XPATH, '//div[@data-testid="description_section"]')[i].text
                    }
                    services.append(service)
                except Exception as error:
                    print(error)
        print("==================☁️☁️services☁️☁️===========")
        print(services)
        print("==================☁️☁️services☁️☁️===========")
        resp_meta["services"] = services
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta['address'] = page.find_element(By.XPATH, '//div[@data-testid="address-component"]').text
        resp_meta['google_link_address'] = page.find_element(By.XPATH, '//div[@class="css-1dbjc4n"]/a').get_attribute("href")
        resp_meta['phone_number'] = page.find_element(By.XPATH, '//div[@class="css-1dbjc4n"]/a/../div').text
        resp_meta['business_hours_sunday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Sunday-value"]').text
        resp_meta['business_hours_monday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Monday-value"]').text
        resp_meta['business_hours_tuesday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Tuesday-value"]').text
        resp_meta['business_hours_wednesday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Wednesday-value"]').text
        resp_meta['business_hours_thursday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Thursday-value"]').text
        resp_meta['business_hours_friday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Friday-value"]').text
        resp_meta['business_hours_saturday'] = page.find_element(By.XPATH, '//div[@data-testid="day-Saturday-value"]').text
        resp_meta['cancellation_policy'] = page.find_element(By.XPATH, '//div[@data-testid="cancellationPolicy--text"]').text
        print(f"resp_meta------------------------------->{resp_meta}")
        time.sleep(2)

        print("==================☁️☁️reviews_page☁️☁️===========")

        page.get(page.current_url)   

        reviews = []
        time.sleep(10)
        try:
            page.find_element(By.XPATH, '//div[@data-testid="tab-navigation-Reviews"]/div').click()
            time.sleep(7)
            for i, elem in enumerate(page.find_elements(By.XPATH, '//div[@data-testid="review__review-container"]')):
                if i < 3:
                    try:
                        review = {
                            "reviews": page.find_elements(By.XPATH, '//div[@data-testid="review-star-summary"]')[i].text,
                            "clientPhotosNo": page.find_elements(By.XPATH, '//h3[@role="heading"]')[i].text,    
                            "review_text": page.find_elements(By.XPATH, '//div[@data-testid="review__review-text"]/div/div')[i].text,
                            "reviewerNameAndDate": page.find_elements(By.XPATH, '//div[@data-testid="review__reviewer-name"]')[i].text,
                            "reviewServiceName": page.find_elements(By.XPATH, '//div[@data-testid="review__service-name"]')[i].text,
                        }
                    except Exception as error:
                        print(error)
                    reviews.append(review)
            print("==================☁️☁️client_adjectives☁️☁️===========")
            print(reviews)
            print("==================☁️☁️client_adjectives☁️☁️===========")
        except Exception as error:
            print(error)

        resp_meta['reviews'] = reviews
        page.get(page.current_url)
        time.sleep(10)

        try:
            page.find_element(By.XPATH, '//div[@data-testid="tab-navigation-About"]/div').click()
            time.sleep(5)
            resp_meta["aboutName"] = [CLEAN_STRING.sub("", elem.text) for elem in page.find_elements(By.XPATH, '//div[@data-testid="pro-greeting"]')]
            resp_meta["joined"] = [elem.text for elem in page.find_elements(By.XPATH, '//div/[@data-testid="provider-info-joined-on-text"]')]
            resp_meta["verifiedAndNoBookedClients"] = [elem.text for elem in page.find_elements(By.XPATH, '//div[@data-testid="profile-highlights-explainer"]')]
            resp_meta["infoAboutMe"] = [elem.text for elem in page.find_elements(By.XPATH, '//div[@data-testid="provider-info-about-me-section"]')]
        except Exception as error:
            print(error)

        try:
            page.get(page.current_url)
            time.sleep(5)
            page.find_element(By.XPATH, '//div[@data-testid="tab-navigation-Products"]/div').click()
            resp_meta["productTitle"] = [elem.text for elem in page.find_elements(By.XPATH, '//div[@data-testid="product-title"]')]
            resp_meta["productDetails"] = [elem.text for elem in page.find_elements(By.XPATH, '//div[@data-testid="expandable-text-content"]')]
        
        except Exception as error:
            print(error)

        if page.current_url:
            resp_meta["gallery_image_urls"] = [elem.get_attribute("src") for elem in page.find_elements(By.TAG_NAME, 'img')]
        time_urls = None
        page.get(page.current_url)
        time.sleep(10)
        try:
            page.find_element(By.XPATH, '//div[@data-testid="tab-navigation-Services"]/div').click()
            time.sleep(10)
            time_urls = [x.get_attribute("href") for x in page.find_elements(By.XPATH, '//a[@data-testid="bookButton"]')] 
            print("==================☁️☁️time_urls☁️☁️===========")
            print(time_urls)
            print("==================☁️☁️time_urls☁️☁️===========")
        except Exception as error:
            print(error)

        date_slots = []
        # Additional logic for date slots can be added here

        print("==================☁️☁️date_slots☁️☁️===========")
        print(date_slots)
        print("==================☁️☁️date_slots☁️☁️===========")

        styleseat_item["response"] = resp_meta
        self.save_item(styleseat_item)
        print(resp_meta)

    def save_item(self, item):
        # Save the item to the database
        ScrappedData.objects.create(
            **item
        )
        print(f"Saving item: {item}")

    def close(self):
        self.driver.quit()



if __name__ == "__main__":
    # Example usage
    scraper = StyleseatScraper(region="NewYork", category="Hair")
    scraper.start_requests()
    scraper.close()
