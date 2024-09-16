import time
import re
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

class GmapsScrapper:
    def __init__(self, search_string,round_number):
        self.search_string = search_string
        self.base_url = "https://www.google.com/maps/search/"
        self.driver_version='121.0.6167.184'
        self.driver = self.initialize_driver()
        self.round_number = round_number

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

    def get_page_url_status_code(self,url, driver):
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

    def generate_gmap_links(self,url,area):
        driver = self.driver
        google_maps_url = (
                url
                + urllib.parse.quote_plus(area)
                + "?hl=en"
        )
        driver.get(google_maps_url)
        links = []
        time.sleep(7)  # Wait for the page to load dynamically
        divSideBar = None
        try:
            divSideBar = driver.find_element(
                By.CSS_SELECTOR, f"div[aria-label='Results for {area}']"
            )
        except NoSuchElementException as err:
            print("************************search box not found**********************************")


        i = 0
        keepScrolling = True
        while keepScrolling:
            time.sleep(3)
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            html = driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
            links_ = divSideBar.find_elements(By.TAG_NAME, "a")
        
                
            for ind, element in enumerate(links_):
                time.sleep(2)
                print("==================☁️☁️☁️☁️☁️links☁️☁️☁️☁️☁️===========")    
                logging.warning(f"link-{ind}=>{element.get_attribute('href')}")
                print("==================☁️☁️☁️☁️☁️links☁️☁️☁️☁️☁️===========")  
                

                if "place" in element.get_attribute("href"):
                    try:
                        links.append(element.get_attribute("href"))
                        # Link.objects.create(url=element.get_attribute("href"),name='gmaps')
                    except Exception as error:
                        print(error)
                    
            if html.find("You've reached the end of the list.") != -1:
                keepScrolling = False
        
        
        driver.quit()

        return links





    def start_requests(self):
        urls = self.generate_gmap_links(self.base_url, self.search_string)

        for url in urls:
            page = self.generate_html(url)
            
            print("==================☁️☁️generated_url☁️☁️===========")
            print(page.current_url)
            print("==================☁️☁️generated_url☁️☁️===========")

            self.driver.get(page.current_url)
            self.parse(self.driver.page_source)

    def parse(self, page_source):
        print("==================☁️☁️titles_page☁️☁️===========")
        resp_meta = {}
        item = {}
        item["name"] = "google_maps"
        item["inference_key"] = self.search_string

        resp_meta["name"] = "google_maps"
        resp_meta["title"] = CLEAN_STRING.sub("", self.driver.title)
        time.sleep(4)
        resp_meta["main_image"] = self.driver.find_element(By.XPATH, '//button[contains(@class,"aoRNLd kn2E5e NMjTrf lvtCsd")]/img').get_attribute("src")
        resp_meta["business_name"] = CLEAN_STRING.sub("", self.driver.find_element(By.XPATH, '//span[contains(@class,"a5H0ec")]/..').text)
        resp_meta["review"] = self.driver.find_element(By.XPATH, '//div[contains(@class,"F7nice")]/span[1]').text
        ig_info = []
        # TODO: attach to process_users

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")

        resp_meta["no_reviews"] = self.driver.find_element(By.XPATH, '//div[contains(@class,"F7nice")]/span[2]').text
        resp_meta["category"] = self.driver.find_element(By.XPATH, '//button[contains(@class,"DkEaL")]').text
        reviews = []

        for i, element in enumerate(self.driver.find_elements(By.XPATH, "//div[@class='jJc9Ad ']")):
            review = {
                "author": self.driver.find_elements(By.XPATH, '//div[contains(@class,"d4r55")]')[i].text,
                "text": self.driver.find_elements(By.XPATH, '//div[contains(@class,"MyEned")]/span')[i].text,
                "rating": self.driver.find_elements(By.XPATH, '//span[contains(@class,"kvMYJc")]')[i].get_attribute("aria-label"),
                "time": self.driver.find_elements(By.XPATH, '//span[contains(@class,"rsqaWe")]')[i].text
            }
            reviews.append(review)

        resp_meta['reviews'] = reviews
        resp_meta["address"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"rogA2c")]/div')]

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")

        resp_meta["days_available"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//tr[contains(@class,"y0skZc")]/td/div')]
        resp_meta["times_available"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//tr[contains(@class,"y0skZc")]/td/ul/li')]

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")

        resp_meta["available_image_works"] = [elem.get_attribute("src") for elem in self.driver.find_elements(By.XPATH, '//img[contains(@class,"DaSXdd")]')]
        resp_meta["testimonial_wordings"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"ZXMsO")]')]
        resp_meta["testimonial_date"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"jrtH8d")]')]

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")

        try:
            resp_meta["is_booking_available"] = self.driver.find_element(By.XPATH, '//a[contains(@class,"A1zNzb")]').get_attribute("href")
            if resp_meta["is_booking_available"]:
                resp_meta["booking_header"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"XVS7ef")]')]
                resp_meta["booking_time"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"BRcyT JaMq2b")]')]
                resp_meta["booking_price"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"BRcyT JaMq2b")]/span')]
                resp_meta["booking_provider"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//div[contains(@class,"NGLLDf")]/span')]
        except Exception as error:
            print("no booking available")

        try:
            self.driver.get(self.driver.current_url)
            time.sleep(2)
            self.driver.find_elements(By.XPATH, '//div[contains(@class,"Gpq6kf fontTitleSmall")]')[1].click()
        except Exception as error:
            print(error)

        time.sleep(5)
        about_url = self.driver.current_url
        if about_url:
            resp_meta["tag_name"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//h2[contains(@class,"iL3Qke")]')]
            resp_meta["tag_detail"] = [elem.text for elem in self.driver.find_elements(By.XPATH, '//li[contains(@class,"hpLkke")]/span')]
        
        item["response"] = resp_meta
        self.save_item(item)

    def save_item(self, item):
        # Save the item to the database
        print(item)
        ScrappedData.objects.create(
            **item
        )
        print(f"Saving item: {item}")

    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    search_string = "Minute Suites - DFW Airport Terminal A, Near A38,TX,US"
    spider = GmapsScrapper(search_string)
    spider.start_requests()
    spider.close_driver()

