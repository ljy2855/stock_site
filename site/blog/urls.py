from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/buy',views.buy_stock, name='buy_stock'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('rank/',views.user_rank, name='user_rank'),
    path('user/',views.user_info,  name = 'user_info'),
    path('signup/',views.sign_up, name = 'sign_up'),
]