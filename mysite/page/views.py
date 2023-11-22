from django.shortcuts import render, get_object_or_404,redirect

from .forms import UserForm
from django.contrib.auth.models import User
from django.contrib import auth
from .models import *
import pymongo
from django.conf import settings

import json
from bson import ObjectId
from datetime import datetime

# ObjectId를 문자열로 변환하는 커스텀 인코더
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, o)

# 데이터를 JSON으로 변환



# Create your views here.
def main_page(request):
    stocks = Stock.objects.all()
    return render(request,'pages/main_page.html',{'pages' : stocks})


def stock_detail(request,pk):
    stock = get_object_or_404(Stock,pk = pk)
    data = get_stock_history(stock)
    # print(data)
    return render(request,'pages/stock_detail.html',{'stock': stock,'data' : data})


def get_stock_history(stock : Stock):
    code = stock.code

    client = pymongo.MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    documents =  db["stock_"+code].find().sort('date',pymongo.ASCENDING)
    json_data = JSONEncoder().encode(list(documents))
    return json_data

def update_stock_from_history(stock :Stock,  history):
    pass
    # last_record = history[-1]
    # last_pre_record = history[-2]
    # stock.current_price = 


def sign_up(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            auth.login(request,new_user)
            return redirect('main_page')
        else:
            return HttpResponse('사용자명이 이미 존재합니다.')
    else :
        form = UserForm()
    return render(request,'auth/signup.html', {'form' : form})