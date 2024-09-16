import logging
import scrapy
import time
import re
import urllib.parse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from .helpers.gmaps_dynamic_actions import generate_gmap_links
from .helpers.utils import click_element,generate_html
from ..http import SeleniumRequest
from ..items import APIItem
from boostedchatScrapper.items import GmapsItem

CLEAN_STRING = re.compile(r"[\']")

class GmapsSpider(CrawlSpider):
    name = "gmaps"
    allowed_domains = ["www.google.com"]
    base_url = "https://www.google.com/maps/search/"
    # start_urls = [
    #     "https://www.google.com/maps/search/"

    # ]

    rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse", follow=True),)



    def __init__(self, search_string, **kwargs):
        self.search_string = search_string # py36
        super().__init__(**kwargs)  # python3
    
    def start_requests(self):
        urls = generate_gmap_links(self.base_url,self.search_string)

        for url in urls:
            page  = generate_html(url)
            
            print("==================☁️☁️generated_url☁️☁️===========")
            print(page.current_url)
            print("==================☁️☁️generated_url☁️☁️===========")
            yield SeleniumRequest(
                    url = page.current_url,
                    callback = self.parse
                )

        # search_string = "Minute Suites - DFW Airport Terminal A, Near A38,TX,US"
        # google_maps_url = (
        #     "https://www.google.com/maps/search/"
        #     + urllib.parse.quote_plus(self.search_string)
        #     + "?hl=en"
        # )
        
        # yield SeleniumRequest(
        #             url = google_maps_url,
        #             callback = self.parse
        #         )
    
    

    def parse(self, response):
        print("==================☁️☁️titles_page☁️☁️===========")
        resp_meta = {}
        item = APIItem()
        item["name"] = "google_maps"
        item["inference_key"] = self.search_string
        resp_meta["name"] = "google_maps"
        resp_meta["title"] = CLEAN_STRING.sub("", response.request.meta['driver'].title)
        time.sleep(4)
        resp_meta["main_image"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//button[contains(@class,"aoRNLd kn2E5e NMjTrf lvtCsd")]/img').get_attribute("src")
        resp_meta["business_name"] = CLEAN_STRING.sub("",response.request.meta['driver'].find_element(by=By.XPATH, value='//span[contains(@class,"a5H0ec")]/..').text)
        resp_meta["review"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[contains(@class,"F7nice")]/span[1]').text
        ig_info = []
        #TODO: attach to process_users
       
        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")
        
        resp_meta["no_reviews"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[contains(@class,"F7nice")]/span[2]').text
        resp_meta["category"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//button[contains(@class,"DkEaL")]').text
        reviews = []
        for i,element in enumerate(response.request.meta['driver'].find_elements(by=By.XPATH, value="//div[@class='jJc9Ad ']")):
            review = {

                "author":response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"d4r55")]')[i].text,
                "text":response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"MyEned")]/span')[i].text,
                "rating":response.request.meta['driver'].find_elements(by=By.XPATH, value='//span[contains(@class,"kvMYJc")]')[i].get_attribute("aria-label"),
                "time":response.request.meta['driver'].find_elements(by=By.XPATH, value='//span[contains(@class,"rsqaWe")]')[i].text
            
            }
            reviews.append(review)

        resp_meta['reviews'] = reviews
        resp_meta["address"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"rogA2c")]/div')]
        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")
        
        resp_meta["days_available"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//tr[contains(@class,"y0skZc")]/td/div')]
        resp_meta["times_available"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//tr[contains(@class,"y0skZc")]/td/ul/li')]

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")
        
        resp_meta["available_image_works"] = [elem.get_attribute("src") for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//img[contains(@class,"DaSXdd")]')]
        resp_meta["testimonial_wordings"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"ZXMsO")]')]
        resp_meta["testimonial_date"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"jrtH8d")]')]

        print("==================☁️☁️resp_meta☁️☁️===========")
        print(f"resp_meta------------------------------->{resp_meta}")
        print("==================☁️☁️resp_meta☁️☁️===========")
        
        try:
            
            resp_meta["is_booking_available"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//a[contains(@class,"A1zNzb")]').get_attribute("href")
            if resp_meta["is_booking_available"]:
                resp_meta["booking_header"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"XVS7ef")]')]
                resp_meta["booking_time"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"BRcyT JaMq2b")]')]
                resp_meta["booking_price"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"BRcyT JaMq2b")]/span')]
                resp_meta["booking_provider"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"NGLLDf")]/span')]
        except Exception as error:
            print("no booking available")

        try:
            response.request.meta['driver'].get(response.url)
            time.sleep(2)
            response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"Gpq6kf fontTitleSmall")]')[1].click() 
        except Exception as error:
            print(error)
        
     
        time.sleep(5)
        about_url = response.request.meta['driver'].current_url
        if about_url:
            resp_meta["tag_name"] =  [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//h2[contains(@class,"iL3Qke")]')]
            resp_meta["tag_detail"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//li[contains(@class,"hpLkke")]/span')]
        item["response"] = resp_meta
        yield item

    def parse_reviews(self,response):
        item = {}
        item["review_names"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"d4r55")]')]
        item["review_content"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//span[contains(@class,"wiI7pd")]')]
        print("==================☁️☁️reviews☁️☁️===========")
        print(f"reviews------------------------------->{item}")
        print("==================☁️☁️reviews☁️☁️===========")
        yield item


    def parse_booking_site(self,response):
        item = {}
        item["booking_header"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"XVS7ef")]')]
        item["booking_time"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"BRcyT JaMq2b")]')]
        item["booking_price"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"BRcyT JaMq2b")]/span')]
        item["booking_provider"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@class,"NGLLDf")]/span')]
        yield item
 
    def parse_about(self,response):
        item = {}
        item["tag_name"] =  [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//h2[contains(@class,"iL3Qke")]')]
        item["tag_detail"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//li[contains(@class,"hpLkke")]/span')]
        yield item


    