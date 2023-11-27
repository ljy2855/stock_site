from datetime import datetime, time, timedelta
import json

from kafka import KafkaConsumer
from .models import *
from bson import ObjectId
import pymongo
from django.conf import settings
import sentry_sdk
import requests

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, o)
    
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE]


def get_stock_history(code):
    with sentry_sdk.start_transaction(name="load chart data"):
        documents =  db["stock_"+code].find().sort('date',pymongo.ASCENDING)
        json_data = JSONEncoder().encode(list(documents))
        return json_data
    

def update_current_stock_state(code,force_update: False):
    """
    realtime stock info update api endpoint
    ---
    check current_time and request scrapyd to crawling current stock state 
    """
    current_time = datetime.now().time()

    # 크롤링을 허용하는 시간 범위 설정
    start_time = time(9, 0)  # 오전 9시
    end_time = time(15, 30)  # 오후 3시 30분

    # 현재 시간이 크롤링을 허용하는 시간 범위 내에 있는지 확인
    if start_time <= current_time <= end_time or force_update:
        URL = 'http://localhost:6800/schedule.json'
        payload = {
            'project' : "default",
            'spider' : 'stock_state_spider',
            'code' : code,
        }
        return requests.post(URL,data=payload)
    else:
        return requests.Response()
    

def check_stock_history_to_update(code):
    with sentry_sdk.start_transaction(name="check day crawling"):
        latest_document = db["stock_"+code].find_one(sort=[('date', pymongo.DESCENDING)])
        if latest_document:
            last_crawled_date = latest_document['date']
            current_date = datetime.utcnow().date()

            # 어제 날짜 계산
            yesterday_date = current_date - timedelta(days=1)

            # 현재 날짜가 평일인지 확인 (0:월요일, 6:일요일)
            is_weekday = current_date.weekday() < 5
            if last_crawled_date.date() <= yesterday_date and is_weekday:
                URL = 'http://localhost:6800/schedule.json'
                payload = {
                    'project' : "default",
                    'spider' : 'day_stock_spider',
                    'code' : code,
                    'target_date' : last_crawled_date.strftime("%Y.%m.%d"),
                }
                requests.post(URL,data=payload)
        else:
            URL = 'http://localhost:6800/schedule.json'
            payload = {
                'project' : "default",
                'spider' : 'day_stock_spider',
                'code' : code,
            }
            requests.post(URL,data=payload)


def set_stock_state(stock : Stock):
    with sentry_sdk.start_transaction(name='update current data'):
        try:
            documents =  db["state_" + stock.code].find().sort('time', pymongo.DESCENDING).limit(1)[0]
            if documents:
                stock.current_price = documents['current_price']
                stock.high_price = documents['high_price']
                stock.low_price = documents['low_price']
                stock.prev_price = documents['prev_price']
                stock.opening_price = documents['opening_price']
                stock.up_down = documents['up_down']
                stock.volume = documents['volume']
                stock.updated_at = documents['time']
                stock.save()
        except IndexError:
            update_current_stock_state(stock.code,force_update=True)
            
