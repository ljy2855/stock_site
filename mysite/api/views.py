from django.http import HttpResponse , JsonResponse
from django.conf import settings
from django.shortcuts import render
from user.models import *
from page.models import *
# Create your views here.
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view
from kafka import KafkaConsumer
from page.crawl_api import *
import json
import requests


@api_view(['GET'])
def update_stock_price(request, pk):
    stock = Stock.objects.get(pk=pk)
    response = update_current_stock_state(stock.code,False)
    if response.status_code == 200:
        consumer = KafkaConsumer(
        "state_" + stock.code,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        for message in consumer:
            # 새로운 메시지 처리
            consumer.close()
            return JsonResponse({'status': 'crawling_finish', 'data' : message.value}, status=200)
    else:
        return HttpResponse({'status': 'crawling_fail'}, status=503)



@api_view(['POST'])
@authentication_classes([BasicAuthentication, TokenAuthentication,SessionAuthentication])
def trade_stock(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)  # 혹은 다른 적절한 응답

    user = request.user
    form_data =request.data
    stock_code = form_data['stock_code']
    quantity = int(form_data['quantity'])
    if quantity >0:
        return purchase_stock(user,stock_code,quantity)
    else:
        return sell_stock(user,stock_code,quantity * -1)
    



def purchase_stock(user, stock_code, quantity):

    stock = Stock.objects.get(code=stock_code)
    profile = UserProfile.objects.get(user=user)

    total_cost = stock.current_price * quantity
    if profile.money >= total_cost:
        profile.money -= total_cost
        profile.save()
        # 주식 구매 처리 (예: 주식 보유 정보 업데이트)
        try:
            holding = HoldingStock.objects.get(user=user,stock=stock)
            holding.cnt += quantity
            holding.save()
        except HoldingStock.DoesNotExist:
            HoldingStock.objects.create(user=user,stock=stock,cnt=quantity)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=501)

def sell_stock(user, stock_code, quantity):
    stock = Stock.objects.get(code=stock_code)
    profile = UserProfile.objects.get(user=user)

    try:
        holding = HoldingStock.objects.get(user=user,stock=stock)
        if holding.cnt >= quantity:

            total_income = stock.current_price * quantity
            profile.money += total_income
            
            holding.cnt -= quantity
            profile.save()
            holding.save()
            if holding.cnt == 0:
                holding.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=502)
            
    except HoldingStock.DoesNotExist:
        return HttpResponse(status=502)

    # 주식 판매 처리 (예: 주식 보유 정보 확인 및 업데이트)
    