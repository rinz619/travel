from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from superadmin import views


app_name = 'superadmin'

urlpatterns = [
    path('',views.index.as_view(),name='login'),
    path('Logout', views.Logout.as_view(), name='Logout'),
    path('profile', views.profile.as_view(), name='profile'),
    path('dashboard', views.dashboard.as_view(), name='dashboard'),

    path('fileuploads', views.fileuploads.as_view(), name='fileuploads'),

    path('agentslist', views.agentslist.as_view(), name='agentslist'),
    path('agentscreate', views.agentscreate.as_view(), name='agentscreate'),
    path('agentsedit/<int:id>', views.agentscreate.as_view(), name='agentsedit'),

    path('offlinebookingslist', views.offlinebookingslist.as_view(), name='offlinebookingslist'),
    path('offlinebookingscreate', views.offlinebookingscreate.as_view(), name='offlinebookingscreate'),
    path('offlinebookingsedit/<int:id>', views.offlinebookingscreate.as_view(), name='offlinebookingsedit'),

    path('accountledger', views.accountledger.as_view(), name='accountledger'),
    path('download-excel/', views.download_excel, name='download_excel'),
    # path('download-pdf/', views.download_pdf, name='download_pdf'),
    
    path('invoice/<str:id>', views.invoice.as_view(), name='invoice'),



    

]