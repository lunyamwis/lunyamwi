import requests
import json
import scrapy
import os
from lxml import etree
from ..items import APIItem
from django.conf import settings
from boostedchatScrapper.models import ScrappedData
from asgiref.sync import sync_to_async


class MindbodySpider(scrapy.Spider):
    name = 'mindbodyonline'
    allowed_domains = ['mindbodyonline.com']

   

    def parse_locations(self, response):
        try:
            xml_content = response.body
        except Exception as err:
            print("xml content not found")
        root = etree.fromstring(xml_content)
        nsmap = root.nsmap
        nsmap['ns'] = nsmap.pop(None)
        item = APIItem()
        for url in root.xpath('//ns:url/ns:loc/text()', namespaces=nsmap):

            url_ = "https://prod-mkt-gateway.mindbody.io/v1/search/locations"
            location = url.split('/')[-1].strip().replace('\n', '')
            
            if len(location) > 2:
                payload = json.dumps({
                "sort": "",
                "page": {
                    "size": 1
                },
                "filter": {
                    "radius": 0,
                    "locationSlugs": [location]
                }
                })
                headers = {
                'Content-Type': 'application/json',
                'Cookie': '__cf_bm=TfUJKbjzA.3gHeKswmI8JEfKeUKVFxcfaboMDPcIX.w-1710923557-1.0.1.1-AiydEiakyZqpfqyi1R0ZCAoaP_R1UHtV7SqwO3PLPKqpxGaoAscFG5RhR8HxV.clUzoJAwuzNa0DIGegqKVWUA'
                }
                try:
                    response = requests.request("POST", url_, headers=headers, data=payload)
                    print(response.json())
                except Exception as error:
                    print(error)
                item['name'] = f'mindbodyonline/locations/{location}'
                item['response'] = response.json()
                
                yield item

    def parse_instructors(self, response):
        try:
            xml_content = response.body
        except Exception as err:
            print("xml content not found")
        root = etree.fromstring(xml_content)
        nsmap = root.nsmap
        nsmap['ns'] = nsmap.pop(None)
        item = APIItem()
        for url in root.xpath('//ns:url/ns:loc/text()', namespaces=nsmap):

            url_ = "https://prod-mkt-gateway.mindbody.io/v1/search/instructors"
            location = url.split('/')[-1].strip().replace('\n', '')
            if len(location) > 2:
                payload = json.dumps({
                "filter": {
                    "locationSlugs": [location]
                }
                })
                headers = {
                'Content-Type': 'application/json',
                'Cookie': '__cf_bm=TfUJKbjzA.3gHeKswmI8JEfKeUKVFxcfaboMDPcIX.w-1710923557-1.0.1.1-AiydEiakyZqpfqyi1R0ZCAoaP_R1UHtV7SqwO3PLPKqpxGaoAscFG5RhR8HxV.clUzoJAwuzNa0DIGegqKVWUA'
                }
                try:
                    response = requests.request("POST", url_, headers=headers, data=payload)
                    print(response.json())
                except Exception as error:
                    print(error)
                item['name'] = f'mindbodyonline/instructors/{location}'
                item['response'] = response.json()
                yield item
    

    def parse_availability(self, response):

        try:
            xml_content = response.body
        except Exception as err:
            print("xml content not found")
        root = etree.fromstring(xml_content)
        nsmap = root.nsmap
        nsmap['ns'] = nsmap.pop(None)
        item = APIItem()
        for url in root.xpath('//ns:url/ns:loc/text()', namespaces=nsmap):
            location = url.split('/')[-1].strip().replace('\n', '')
            url_ = f"https://prod-mkt-gateway.mindbody.io/v1/availability/location?filter.location_slug={location}&filter.timezone=America%2FLos_Angeles&filter.start_time_from=2024-03-19T11%3A04%3A18.927Z&filter.start_time_to=2024-04-09T06%3A59%3A59.999Z"
            if len(location) > 2:
                params = json.dumps({
                "filter": {
                    "locationSlugs": [location]
                }
                })
                headers = {
                'Content-Type': 'application/json',
                'Cookie': '__cf_bm=TfUJKbjzA.3gHeKswmI8JEfKeUKVFxcfaboMDPcIX.w-1710923557-1.0.1.1-AiydEiakyZqpfqyi1R0ZCAoaP_R1UHtV7SqwO3PLPKqpxGaoAscFG5RhR8HxV.clUzoJAwuzNa0DIGegqKVWUA'
                }
                try:
                    response = requests.request("GET", url_, headers=headers, params=params)
                    print(response.json())
                except Exception as error:
                    print(error)
                item['name'] = f'mindbodyonline/availability/{location}'
                item['response'] = response.json()
                yield item



        
    def start_requests(self):
    
        # Define the directory containing XML files
        xml_directory = settings.BASE_DIR/'sitemaps'

        # Fetch all XML files from the directory
        xml_files = [f for f in os.listdir(xml_directory) if f.endswith('.xml')]

        # Construct start_urls
        start_urls = [f'file://{xml_directory}/{filename}' for filename in xml_files]
        # start_urls = [
            # f'file:///home/martin/Documents/boostedchat-scrapper/https___www_mindbodyonline_com_explore_sitemap1_xml_gz.xml',
            # f'file:///home/martin/Documents/boostedchat-scrapper/https___www_mindbodyonline_com_explore_sitemap2_xml_gz.xml'
        # ]

        for url in start_urls:
            yield scrapy.Request(url, callback=self.parse_instructors, dont_filter=True)
            yield scrapy.Request(url, callback=self.parse_availability, dont_filter=True)
            yield scrapy.Request(url, callback=self.parse_locations, dont_filter=True)