# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy_djangoitem import DjangoItem
from boostedchatScrapper.models import ScrappedData
import scrapy


class BoostedchatscrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GmapsItem(scrapy.Item):
    name = scrapy.Field()
    resp_meta = scrapy.Field()
    
class StyleSeatItem(scrapy.Item):
    name = scrapy.Field()
    resp_meta = scrapy.Field()
    
# items.py


class APIItem(DjangoItem):
    django_model = ScrappedData
    