from typing import Any, Iterable, Optional
import scrapy
from pathlib import Path

from scrapy.http import Request

class DayStockSpider(scrapy.Spider):
    name = 'day_stock_spider'
    base_url = 'https://finance.naver.com/item/sise_day.naver'
    start_urls = ['https://finance.naver.com/item/sise_day.naver?code=000660&page=1']

    def __init__(self, **kwargs: Any):
        self.code = '000660'
        self.field = {'date','closing_price','market_price','high_price','low_price','amount'}

    def start_requests(self) -> Iterable[Request]:

        
        self.page = 1
        url = self.base_url + '?code={}&page={}'.format(self.code,self.page)

        yield scrapy.Request(url)

    def parse(self, response):
        # 각 와인의 컨테이너를 반복
        # print(response.body)
        # print(response.css('table.type2 tr'))
        self.page +=1

        for row in response.css('table.type2 tr'):
            date = row.css('td:nth-child(1) span::text').get()

            if date == None:
                continue
            yield{
                'date' : date,
                'closing_price' : row.css('td:nth-child(2) span::text').get(),
                'market_price' : row.css('td:nth-child(4) span::text').get(),
                'high_price' : row.css('td:nth-child(5) span::text').get(),
                'low_price' : row.css('td:nth-child(6) span::text').get(),
                'amount' : row.css('td:nth-child(7) span::text').get(),
            }
            next_page = response.css("td.pgR a::attr(href)").get()
            if next_page and self.page < 20:
                next_url = response.urljoin(next_page)
                yield scrapy.Request(next_url)
            
 
   

        # 다음 페이지로 이동하는 로직 (필요한 경우)
        # next_page = response.css('a.next_page::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)
