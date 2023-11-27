from typing import Any, Iterable, Optional
import scrapy
from pathlib import Path

from scrapy.http import Request

class DayStockSpider(scrapy.Spider):
    name = 'day_stock_spider'
    base_url = 'https://finance.naver.com/item/sise_day.naver'
    
    # start_urls = ['https://finance.naver.com/item/sise_day.naver?code=000660&page=1']

    def __init__(self, code=None, cnt=40, target_date=None, *args, **kwargs):
        super(DayStockSpider, self).__init__(*args, **kwargs)
        assert(code != None)
        self.code = code
        self.cnt = cnt
        self.target_date = target_date
        self.collection_name = 'stock_' + self.code
        self.field = {'date','closing_price','market_price','high_price','low_price','amount'}

    def start_requests(self) -> Iterable[Request]:

        
        self.page = 1
        url = self.base_url + '?code={}&page={}'.format(self.code,self.page)

        yield scrapy.Request(url)

    def parse(self, response):
       
        self.page +=1

        for row in response.css('table.type2 tr'):
            date = row.css('td:nth-child(1) span::text').get()

            if date == None:
                continue
            if date == self.target_date:
                return
            yield{
                'date' : date,
                'closing_price' : row.css('td:nth-child(2) span::text').get(),
                'market_price' : row.css('td:nth-child(4) span::text').get(),
                'high_price' : row.css('td:nth-child(5) span::text').get(),
                'low_price' : row.css('td:nth-child(6) span::text').get(),
                'amount' : row.css('td:nth-child(7) span::text').get(),
            }
            
        if self.page < self.cnt:
            next_url = self.base_url + '?code={}&page={}'.format(self.code,self.page)
            yield scrapy.Request(next_url)
            
 

