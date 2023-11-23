from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.main_page,name='main_page'),
    path('stock/<int:pk>/',views.stock_detail,name='stock_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/',views.sign_up, name = 'sign_up'),
    path('rank/',views.user_rank, name='user_rank'),
]