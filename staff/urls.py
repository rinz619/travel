from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from staff import views


app_name = 'staff'

urlpatterns = [
    path('',views.index.as_view(),name='login'),
]