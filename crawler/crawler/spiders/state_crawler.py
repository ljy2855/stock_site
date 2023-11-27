from pathlib import Path
from typing import Any, Iterable, Optional
import scrapy

from kafka import KafkaProducer
import json

from scrapy.http import Request, HtmlResponse

class StateSpider(scrapy.Spider):
    name = 'stock_state_spider'
    base_url = 'https://finance.naver.com/item/sise_day.naver'
    
    # start_urls = ['https://finance.naver.com/item/sise_day.naver?code=000660&page=1']

    def __init__(self, code=None, *args, **kwargs):
        super(StateSpider, self).__init__(*args, **kwargs)
        self.code = code
        self.collection_name = 'state_' + self.code
    
        self.field = {
            "current_price" ,
            "prev_price" ,
            "high_price" ,
            "low_price" ,
            "opening_price" ,
            "volume",
        }


    def start_requests(self) -> Iterable[Request]:
        info_url = 'https://finance.naver.com/item/main.naver?code=' + self.code
        yield scrapy.Request(info_url)

    def parse(self, response, **kwargs: Any) -> Any:
        info = response.css("div.rate_info")
        
        
        current_price = info.css("p.no_today span.blind::text").get()
      
        # 전일 가격 추출
        prev_price = info.css('table.no_info tr:nth-of-type(1) td.first span.blind::text').get()

        # 고가 추출
        high_price = info.css('table.no_info tr:nth-of-type(1) td:nth-child(2) em span.blind::text').get()

        # 저가 추출
        low_price = info.css('table.no_info tr:nth-of-type(2) td:nth-child(2) em span.blind::text').get()

        # 시가 추출
        opening_price = info.css('table.no_info tr:nth-of-type(2) td.first em span.blind::text').get()

        # 거래량 추출
        volume = info.css('table.no_info tr:nth-of-type(1) td:nth-child(3) em span.blind::text').get()
        
        
        yield{
            "current_price" : current_price,
            "prev_price" : prev_price,
            "high_price" : high_price,
            "low_price" : low_price,
            "opening_price" : opening_price,
            "volume" : volume,
        }
        