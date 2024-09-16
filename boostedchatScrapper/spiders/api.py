import scrapy
import json
import time
from scrapy.exceptions import CloseSpider
from ..items import APIItem

class ApiSpider(scrapy.Spider):
    name = 'api'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 40


    def start_requests(self):
        for i in range(5):
            time.sleep(2)
            page_number = self.counter
            headers = {
                'Accept':'application/vnd.api+json',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'en-US,en;q=0.9',
                'Content-Type':'application/vnd.api+json',
                'Dnt':'1',
                'Origin':'https://www.mindbodyonline.com',
                'Sec-Ch-Ua':'"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                'Sec-Ch-Ua-Mobile':'?0',
                'Sec-Ch-Ua-Platform':'"Linux"',
                'Sec-Fetch-Dest':'empty',
                'Sec-Fetch-Mode':'cors',
                'Sec-Fetch-Site':'cross-site',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'X-Mb-App-Build':'2024-03-04T05:46:17.903Z',
                'X-Mb-App-Name':'mindbody.io',
                'X-Mb-App-Version':'5086085a',
                'X-Mb-User-Session-Id':'oeu1710165582529r0.8416210522241039'
            }
            data = {'sort':'-_score,distance','page':{'size':500,'number':page_number},'filter':{'categories':[],'radius':-1,'term':'','cmMembershipBookable':'any','latitude':47.60150146484375,'longitude':-122.3303985595703,'categoryTypes':[]}}
            url = f'https://prod-mkt-gateway.mindbody.io/v1/search/locations'
            # url = "https://prod-mkt-gateway.mindbody.io/v1/availability/location?filter.location_slug=washington-athletic-club&filter.timezone=America%2FLos_Angeles&filter.start_time_from=2024-03-12T08%3A17%3A56.136Z&filter.start_time_to=2024-04-02T06%3A59%3A59.999Z"
            yield scrapy.Request(url,headers=headers,
                                body=json.dumps(data))
                                # meta={'proxy':f"http://Sql8t2uRG3XRvQrO:wifi;ke;starlink;;nairobi@proxy.soax.com:9000"})
            
            self.counter += 1
            
        
    def parse(self, response):
        print('this is response', response)
        api_item = APIItem()
        dictionaries = response.json()
        for i,dictionary in enumerate(dictionaries['data']):
            api_item['name'] = f'mindbodyonline_api_{i}'
            api_item['response'] = dictionary
        
            yield api_item