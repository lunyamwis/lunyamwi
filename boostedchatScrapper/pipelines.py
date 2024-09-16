# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import json
from itemadapter import ItemAdapter
# from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from boostedchatScrapper.models import ScrappedData
from asgiref.sync import sync_to_async

Base = declarative_base()


class BoostedchatscrapperPipeline(object):
    async def process_item(self, item, spider):
        # Convert synchronous operation to asynchronous using sync_to_async
        create_scraped_data = sync_to_async(ScrappedData.objects.create)

        # Await the asynchronous function call
        
        await create_scraped_data(name=item['name'], inference_key=item.get('inference_key',''),response=item['response'])

        return item