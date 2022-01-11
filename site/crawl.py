#!/home/ec2-user/environment/myvenv/bin/python
import pandas as pd 
import calendar
import os
import time
import datetime
import sys
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
django.setup()
from blog.models import *
from django.shortcuts import get_object_or_404
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import requests
from bs4 import BeautifulSoup
from django.utils import timezone



stock_code = {'SK' : '000660', 'KAKAO' : '035720', 'NAVER' : '035420',
			  '삼성전자' : '005930','SAMSUNG_SDI' :'006400', 'LG화학' : '051910',
             '삼성바이오' : '207940', '삼성전자우' : '005935', '삼성바이오로직스' : '207940',
			 '셀트리온' : '068270', '현대차' : '005380'}
today = time.strftime('%Y%m%d%H%M00',time.localtime(time.time()))
date = timezone.datetime.strptime(today,'%Y%m%d%H%M%S')


holiday_list = ['20210211','20210211','20210212','20210301','20210505','20210519',
				'20210920','20210921','20210922','20211231']
				
def CrawlStock(name,try_cnt):

	code = stock_code[name]
	
	try :
		stock = StockData.objects.get(name = name)
	except StockData.DoesNotExist:
		StockData.objects.create(name = name)

	try:
		stock = StockData.objects.get(name = name,time = date)
		print("already update")
	except StockData.DoesNotExist:
		try:
			url = "http://asp1.krx.co.kr/servlet/krx.asp.XMLSiseEng?code={code}".format(code = code)
			print(url)
			req=urlopen(url)
			result=req.read()
			xmlsoup=BeautifulSoup(result,"lxml-xml")
			temp = xmlsoup.find("TBL_StockInfo")
			CurJuka = int(temp['CurJuka'].replace(",",""))
			PrevJuka = int(temp['PrevJuka'].replace(",",""))
			HighJuka = int(temp['HighJuka'].replace(",",""))
			LowJuka = int(temp['LowJuka'].replace(",",""))
			stock = StockData.objects.get(name = name)
			stock.price = CurJuka
			stock.pre_price = PrevJuka
			stock.high_price = HighJuka
			stock.low_price = LowJuka
			stock.time = date
			stock.save()
			StockHistory.objects.create(name = name, price = CurJuka, time = date)
			print(name + " krx update")
		except ValueError as e:
			if try_cnt <= 3:
				time.sleep(0.5)
				CrawlStock(name,try_cnt+1)
			if try_cnt is 4 :
				url = "https://finance.naver.com/item/main.nhn?code={code}".format(code = code)
				res = requests.get(url)
				soup = BeautifulSoup(res.text, 'html.parser')
				today = soup.select_one('#chart_area > div.rate_info > div')
				price = today.select_one('.blind').text.replace(",","")
				today = soup.select_one('#chart_area > div.rate_info > table.no_info')
				value = today.select(".blind")
				PrevJuka = int(value[0].text.replace(",",""))
				HighJuka = int(value[1].text.replace(",",""))
				LowJuka = int(value[5].text.replace(",",""))
				stock = StockData.objects.get(name = name)
				stock.price = int(price)
				stock.pre_price = PrevJuka
				stock.high_price = HighJuka
				stock.low_price = LowJuka
				stock.time = date
				stock.save()
				StockHistory.objects.create(name = name, price = int(price), time = date)
				print(name + " naver update")
		
			
		
		
		
		
		
		
		
		



	
def CrawlCron():
	today = time.strftime('%Y%m%d%H%M00',time.localtime(time.time()))
	date = timezone.datetime.strptime(today,'%Y%m%d%H%M%S')
	if calendar.weekday(2021,int(today[4:6]),int(today[6:8])) <= 4 : # 평일인지 확인
		if int(today[8:10]) >= 9 and int(today[8:10]) <= 17:
			if not( today[0:8] in holiday_list):
				for name in stock_code.keys():
					CrawlStock(name,0)
					time.sleep(0.5)
	
	
if __name__ == "__main__":
	if len(sys.argv) is 2 : #직접 날짜 입력시 그날의 데이터 크롤
		today = sys.argv[1]
		date = timezone.datetime.strptime(today,'%Y%m%d%H%M%S')
	print(today)
	#CrawlCron()

	if calendar.weekday(2021,int(today[4:6]),int(today[6:8])) <= 4 : # 평일인지 확인
		if int(today[8:10]) >= 9 and int(today[8:10]) <= 17:
			if not( today[0:8] in holiday_list):
				for name in stock_code.keys():
					CrawlStock(name,0)
					time.sleep(0.5)

	