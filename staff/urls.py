from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from staff import views


app_name = 'staff'

urlpatterns = [
    path('',views.index.as_view(),name='login'),
    path('home',views.home.as_view(),name='home'),
    path('add_to_login',views.add_to_login,name='add_to_login'),
]