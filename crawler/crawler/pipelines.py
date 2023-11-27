# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import logging
from itemadapter import ItemAdapter
import pymongo
import datetime
from scrapy import signals
from kafka import KafkaProducer



class PreProcessPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        return pipeline

    def spider_opened(self, spider):
        self.spider_name = spider.name
        logging.info(f"Opened spider: {spider.name}")

    def process_item(self, item, spider):
        if spider.name == "day_stock_spider":
            fields = spider.field
            for field in fields:
                if field == 'date':
                    item[field] = datetime.datetime.strptime(item[field],"%Y.%m.%d")
                else:
                    item[field] = int(item[field].replace(',',''))
            
        elif spider.name == "stock_state_spider":
            fields = spider.field
            for field in fields:
                item[field] = int(item[field].replace(',',''))
            item['time'] = datetime.datetime.now()
            item['up_down'] = (item['current_price'] - item['prev_price']) /item['prev_price'] *100

        return item


class MongoPipeline(object):
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.collection_name = spider.collection_name
        self.db = self.client[self.mongo_db]
        # self.db[self.collection_name].drop()


    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
   
        # MongoDB에 저장
        self.db[self.collection_name].insert_one(dict(item))
        logging.info(f"save to Mongo DB")
        return item

class KafkaPipeline(object):
    

        

    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        return pipeline
    


    def spider_opened(self, spider):
        self.spider_name = spider.name
        self.collection_name = spider.collection_name
        
       

        logging.info(f"Opened spider: {spider.name}")

    def process_item(self, item, spider):
        if spider.name == "stock_state_spider":
            producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            message = {'task': 'start_crawling', 'data': item}
            producer.send(self.collection_name, value=message)
            producer.flush()

        return item