import logging
import scrapy
import time
import re
import math

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import HtmlResponse
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By
from boostedchatScrapper.items import StyleSeatItem, APIItem
from urllib.parse import urlparse, parse_qs
from .helpers.styleseat_dynamic_actions import generate_styleseat_links
from .helpers.utils import click_element,generate_html
from ..http import SeleniumRequest

CLEAN_STRING = re.compile(r"[\']")

class StyleseatSpider(CrawlSpider):
    name = "styleseat"
    allowed_domains = ["www.styleseat.com"]
    base_url = "https://www.styleseat.com/m/"
    start_urls = [
        "https://www.styleseat.com/m/v/gerard",
        "https://www.styleseat.com/m/v/barberpaul",
    ]
    start_url = "https://www.styleseat.com/m/v/gerard"

    rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse", follow=True),)

    def __init__(self, region, category, **kwargs):
        self.region = region # py36
        self.category = category
        super().__init__(**kwargs)  # python3
    
    def start_requests(self):
        urls = generate_styleseat_links(f"https://www.styleseat.com/m/search/{self.region}/{self.category}")

        for url in urls:
            page  = generate_html(url)
            
            print("==================☁️☁️generated_url☁️☁️===========")
            print(page.current_url)
            print("==================☁️☁️generated_url☁️☁️===========")
            yield SeleniumRequest(
                    url = page.current_url,
                    callback = self.parse
                )
   

    def parse(self, response):
        styleseat_item = APIItem()
        resp_meta = {}
        print("==================☁️☁️meta_driver☁️☁️===========")
        print(response.request.meta)
        print("==================☁️☁️meta_driver☁️☁️===========")
        time.sleep(10)
        styleseat_item["name"] = "styleseat"
        styleseat_item["inference_key"] = self.region
        resp_meta["name"] = "styleseat"
        resp_meta["secondary_name"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//h1[@data-testid="proName"]').text
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta["logo_url"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[contains(@class,"avatar-icon")]').get_attribute("style")
        resp_meta["profileUrl"] = response.url
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta["category"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="proProfession"]').text
        try:
            resp_meta["igname"] = response.request.meta['driver'].find_element(by=By.XPATH, value='///div[@data-testid="instagram-link"]/div[2]').text
        except Exception as error:
            print(error)
        resp_meta["businessName"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="proBusinessName"]').text
        resp_meta["ratings"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="rating-stars"]').text
        # //div[@data-testid="service-card"]
        time.sleep(7)
        services = []
        for i,elem in enumerate(response.request.meta['driver'].find_elements(by=By.XPATH,value='//div[@data-testid="service-card"]')):
            if i < 3:
                try:
                    service = {
                        "serviceTitle":response.request.meta['driver'].find_elements(by=By.XPATH, value='//h4[@data-testid="serviceTitle"]')[i].text,
                        "serviceDetails":response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="serviceDetails"]')[i].text,
                        "descriptionSection":response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="description_section"]')[i].text
                    }

                    services.append(service)
                except Exception as error:
                    print(error)
        print("==================☁️☁️services☁️☁️===========")
        print(services)
        print("==================☁️☁️services☁️☁️===========")
        resp_meta["services"] = services
        print(f"resp_meta------------------------------->{resp_meta}")
        resp_meta['address'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="address-component"]').text
        resp_meta['google_link_address'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@class="css-1dbjc4n"]/a').get_attribute("href")
        resp_meta['phone_number'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@class="css-1dbjc4n"]/a/../div').text
        resp_meta['business_hours_sunday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Sunday-value"]').text
        resp_meta['business_hours_monday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Monday-value"]').text
        resp_meta['business_hours_tuesday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Tuesday-value"]').text
        resp_meta['business_hours_wednesday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Wednesday-value"]').text
        resp_meta['business_hours_thursday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Thursday-value"]').text
        resp_meta['business_hours_friday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Friday-value"]').text
        resp_meta['business_hours_saturday'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="day-Saturday-value"]').text
        resp_meta['cancellation_policy'] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="cancellationPolicy--text"]').text
        print(f"resp_meta------------------------------->{resp_meta}")
        time.sleep(2)

        print("==================☁️☁️reviews_page☁️☁️===========")
        
        response.request.meta['driver'].get(response.url)   
        
        reviews = []
        time.sleep(10)
        try:
        
            response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="tab-navigation-Reviews"]/div').click()
            time.sleep(7)
            # import pdb;pdb.set_trace()
            for i,elem in enumerate(response.request.meta['driver'].find_elements(by=By.XPATH,value='//div[@data-testid="review__review-container"]')):
                if i < 3:
                    try:
                        review = {
                            "reviews" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review-star-summary"]')[i].text,
                            "clientPhotosNo" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//h3[@role="heading"]')[i].text,    
                            "review_text" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__review-text"]/div/div')[i].text,
                            # "aboutClientAdjectives" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__about-provider"]')[i].text,
                            # "aboutClientLocation" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__about-location"]')[i].text,
                            "reviewerNameAndDate" :response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__reviewer-name"]')[i].text,
                            "reviewServiceName" : response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__service-name"]')[i].text,
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
        response.request.meta['driver'].get(response.url)
        time.sleep(10)
        
        try:
            response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="tab-navigation-About"]/div').click()
            time.sleep(5)
            resp_meta["aboutName"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="pro-greeting"]')]
            resp_meta["joined"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div/[@data-testid="provider-info-joined-on-text"]')]
            resp_meta["verifiedAndNoBookedClients"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="profile-highlights-explainer"]')]
            resp_meta["infoAboutMe"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="provider-info-about-me-section"]')]
        except Exception as error:
            print(error)

        try:
            response.request.meta['driver'].get(response.url)
            time.sleep(5)
            response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="tab-navigation-Products"]/div').click()
            resp_meta["productTitle"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="product-title"]')]
            resp_meta["productDetails"] = [elem.text for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="expandable-text-content"]')]
        
        except Exception as error:
            print(error)

        if response.url:
            resp_meta["gallery_image_urls"] = [elem.get_attribute("src") for elem in response.request.meta['driver'].find_elements(by=By.TAG_NAME, value='img')]
        time_urls = None
        response.request.meta['driver'].get(response.url)
        time.sleep(10)
        time
        try:
            response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="tab-navigation-Services"]/div').click()
            time.sleep(10)
            time_urls = [x.get_attribute("href") for x in response.request.meta['driver'].find_elements(by=By.XPATH, value='//a[@data-testid="bookButton"]')] 
            print("==================☁️☁️time_urls☁️☁️===========")
            print(time_urls)
            print("==================☁️☁️time_urls☁️☁️===========")
        except Exception as error:
            print(error)

        date_slots = []
        # for url in time_urls[0:1]:
        #     time.sleep(7)
        #     response.request.meta['driver'].get(url)
        #     time.sleep(7)
        #     try:
        #         import pdb;pdb.set_trace() 
        #         for available_date in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="sunshine-dot"]/../../../div'):
        #             available_date.click()
        #             time.sleep(7)
        #             try:
        #                 date_slot = {
        #                     "date": available_date.text,
        #                     "available":[el.text for el in available_date.find_elements(by=By.XPATH,value='//button[@class="ss-button medium text-light"]') if el.text != "Notify"],
        #                     "booked":[el.text for el in available_date.find_elements(by=By.XPATH,value=f'//div[contains(@data-testid,"bookedtimepill")]/div')]
        #                 }
        #                 date_slots.append(date_slot)
        #             except Exception as error:
        #                 print(error)
                        
        #             time.sleep(5)
        #             response.request.meta['driver'].get(url)
        #             time.sleep(7)


        #     except Exception as error:
        #         print(error)

        # print("==================☁️☁️date_slots☁️☁️===========")
        # print(date_slots)
        # print("==================☁️☁️date_slots☁️☁️===========")

        # resp_meta["date_slots"] = date_slots

        # averages_one = []
        # try:
        #     for date_slot in date_slots:
        #         averages_one.append((len(date_slot["booked"])/(len(date_slot["booked"])+len(date_slot["available"])))*100)

        #     average = math.ceil(sum(averages_one)/len(averages_one))

        #     if average > 70:
        #         resp_meta["calendar_availability"] = "Fully Booked Calendar"
        #     elif average > 34 and average < 70:
        #         resp_meta["calendar_availability"] = "Some Calendar Availability"
        #     elif average < 34:
        #         resp_meta["calendar_availability"] = "Empty Calendar"
        # except Exception as error:
        #     print(error)
        
        styleseat_item["response"] = resp_meta

        yield resp_meta
        

    def parse_dates(self,response):
        item = {}
        item["availableDates"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="sunshine-dot"]/../../../div')]
        item["unavailableDates"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[contains(@style, "text-decoration-line: line-through;")]/../../../div')]
        yield item


    def parse_reviews(self,response):
        item = {}
        item["reviews"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//div[@data-testid="review-star-summary"]').text
        item["clientPhotosNo"] = response.request.meta['driver'].find_element(by=By.XPATH, value='//h3[@role="heading"]').text
        
            
        item["aboutClientAdjectives"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__about-provider"]')]
        item["aboutClientLocation"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__about-location"]')]
        item["reviewerNameAndDate"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__reviewer-name"]')]
        item["reviewServiceName"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="review__service-name"]')]
        
        yield item
 
    def parse_about(self,response):
        item = {}
        try:
            item["aboutName"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="pro-greeting"]')]
            item["joined"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div/[@data-testid="provider-info-joined-on-text"]')]
            item["verifiedAndNoBookedClients"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="profile-highlights-explainer"]')]
            item["infoAboutMe"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="provider-info-about-me-section"]')]
        except Exception as error:
            print(error)
        yield item


    def parse_products(self,response):
        item = {}
        item["productTitle"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="product-title"]')]
        item["productDetails"] = [CLEAN_STRING.sub("",elem.text) for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="expandable-text-content"]')]
        yield item


    def parse_client_images(self,response):
        item = {}
        item["client_image_urls"] = [elem.get_attribute("src") for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="modal-box-scroll-view"]//img')]
        yield item

    def parse_gallery(self,response):
        item = {}
        item["gallery_image_urls"] = [elem.get_attribute("src") for elem in response.request.meta['driver'].find_elements(by=By.XPATH, value='//div[@data-testid="modal-box-scroll-view"]//img')]
        yield item
