from datetime import datetime
import json
from .models import *
from bson import ObjectId
import pymongo
from django.conf import settings
import sentry_sdk

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

def set_stock_state(stock : Stock):
    with sentry_sdk.start_transaction(name='update current data'):
        documents =  db["state_"+stock.code].find_one()
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
    