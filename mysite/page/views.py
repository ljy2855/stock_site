from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404,redirect

from .forms import UserForm
from django.contrib.auth.models import User
from django.contrib import auth
from .models import *
from .crawl_api import *
from user.models import *


# ObjectId를 문자열로 변환하는 커스텀 인코더


# 데이터를 JSON으로 변환



# Create your views here.
def main_page(request):
    stocks = Stock.objects.all()
    return render(request,'pages/main_page.html',{'pages' : stocks})


def stock_detail(request,pk):
    stock = get_object_or_404(Stock,pk = pk)
    data = get_stock_history(stock.code)
    set_stock_state(stock)
    # print(data)
    return render(request,'pages/stock_detail.html',{'stock': stock,'data' : data})


def user_rank(request):
    user_list = UserProfile.objects.all()
    for user_temp in user_list :
        user_temp.update_total_balance()
   
    return render(request, 'pages/user_rank.html',{'user_list': user_list.order_by('-total_balance') })




def sign_up(request):
    context = {}
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            auth.login(request,new_user)
            return redirect('main_page')
        else:
            context['error'] = '사용자명이 이미 존재합니다.'
    else :
        form = UserForm()
    context['form'] = form
    return render(request,'auth/signup.html', context)