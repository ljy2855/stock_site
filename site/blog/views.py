from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import  HoldingStock, StockData, User_Profile, StockHistory
from .forms import PostForm , UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
import json


def get_holdingstock(request):
    cur_user = request.user
    if cur_user.is_authenticated:
        stock_list = HoldingStock.objects.filter(user = request.user)
        return stock_list
    else:
        return None


def post_list(request):
    stock_list = StockData.objects.all()
    return render(request, 'blog/post_list.html', {'stock_list': stock_list,'holding_stocks': get_holdingstock(request)})


def user_info(request):
    stock_list = HoldingStock.objects.filter(user = request.user)
    # TODO 1

def user_rank(request):
    user_list = User_Profile.objects.all()
    for user_temp in user_list :
        holding_stocks = HoldingStock.objects.filter(user = user_temp.user)
        for stock_temp in holding_stocks:
            user_temp.money += stock_temp.price * stock_temp.cnt
    user_list.order_by('money')
    return render(request, 'blog/user_rank.html',{'user_list': user_list, 'holding_stocks': get_holdingstock(request)})


def post_detail(request, pk):
    stock = get_object_or_404(StockData, pk = pk)
    
    
    price_list = list()
    time_list = list()
    mean_5day_list = list()
    mean_50day_list = list()
    # Chartit 없이 직접 json 데이터 넘기기
    dataset = StockHistory.objects.filter(name = stock.name).order_by('time')
    cnt = 0
    idx = 0
    sum_of_50day = 0
    
    for data in dataset:
        mean_of_5day = 0
        
        if idx >= 4 :
            for cnt in range(0,5) :
                mean_of_5day += dataset[idx-cnt].price
                cnt +=1
            mean_of_5day /= 5

            
        if idx >= 49 :
            if idx is 49:
                for cnt in range(0,50):
                    sum_of_50day += dataset[cnt].price
            else :
                sum_of_50day += data.price
                sum_of_50day -= dataset[idx - 50].price
        
        if mean_of_5day is not 0 :
            mean_5day_list.append([data.time.timestamp()*1000 + 9 * 60 * 60 * 1000, mean_of_5day])
        if sum_of_50day is not 0 :
            mean_50day_list.append([data.time.timestamp()*1000 + 9 * 60 * 60 * 1000, sum_of_50day/50])
        price_list.append([data.time.timestamp()*1000 + 9 * 60 * 60 * 1000, data.price])
        idx += 1
        cnt = 0
        
    #https://www.geeksforgeeks.org/data-visualization-using-chartjs-and-django/
    chart = {
        'chart' : {'type' : 'line'},
        'time' : {'timezoneOffset': '0'},
        'mapNavigation' : {
            'enableMouseWheelZoom' : 'true'
        },

        'rangeSelector' : {
            'selected' : 2
        },
        'title' : {'text' : 'Stock Price'},
        'yAxis' : {'title': {'text' : 'Price'}},
        'xAxis': {'title': {'text': 'time'}
                 },
        'series' : [
            {
                'name' : 'Price',
                'data' : price_list,
                'id' : "base"
            },
            {
                'name' : '5day',
                'data' : mean_5day_list,
            },
            {
                'name' : '50day',
                'data' : mean_50day_list,
            }
            
        ],
        
       
    }
    dump = json.dumps(chart)
    

    return render(request, 'blog/post_detail.html', {'stock' : stock,'holding_stocks': get_holdingstock(request),'chart_json' : dump})
  

def sign_up(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            auth.login(request,new_user)
            return redirect('post_list')
        else:
            return HttpResponse('사용자명이 이미 존재합니다.')
    else :
        form = UserForm()
    return render(request,'registration/signup.html', {'form' : form})



def buy_stock(request, pk):
    stock_data = get_object_or_404(StockData,pk= pk)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            hold_temp = form.save(commit=False)
            try:
                stock_temp = HoldingStock.objects.get(name = stock_data.name ,user = request.user)
                if int(hold_temp.cnt + stock_temp.cnt) < 0 :
                    form = PostForm(instance = HoldingStock)
                    return render(request, 'blog/buy_stock.html', {'form' : form})
                stock_temp.cnt += hold_temp.cnt
                stock_temp.total_price += hold_temp.cnt * stock_data.price
                request.user.user_profile.money -= hold_temp.cnt * stock_data.price
                request.user.user_profile.save()
                if int(stock_temp.cnt) is 0 :
                    stock_temp.delete()
                else:
                    stock_temp.save()

            except HoldingStock.DoesNotExist:
                                
                if hold_temp.cnt <= 0:
                    form = PostForm(instance = HoldingStock)
                    return render(request, 'blog/buy_stock.html', {'form' : form})
                hold_temp.name = stock_data.name
                hold_temp.price = stock_data.price
                hold_temp.user = request.user
                hold_temp.total_price = stock_data.price * hold_temp.cnt
                request.user.user_profile.money -= stock_data.price * hold_temp.cnt
                request.user.user_profile.save()
                hold_temp.save()
            return redirect('post_detail',pk = stock_data.pk)
    else :
        form = PostForm(instance = HoldingStock)
    return render(request, 'blog/buy_stock.html', {'form' : form,'stock_data' : stock_data,'holding_stocks': get_holdingstock(request)})
    
'''
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request,pk):
    post = get_object_or_404(Post, pk =pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance = post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail',pk = post.pk)
    else :
        form = PostForm(instance = post)
    return render(request, 'blog/post_edit.html', {'form' : form})
@login_required
def post_delete(request,pk):
    post = get_object_or_404(Post, pk = pk)
    post.delete()
    return redirect('post_list')
'''
# Create your views here.
