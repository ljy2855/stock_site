from django.contrib import admin
from django.urls import path , include
from . import views
urlpatterns = [
     path('trade/',views.trade_stock, name = 'trade_stock'),
]
