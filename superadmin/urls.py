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



    path('bannerlist', views.bannerlist.as_view(), name='bannerlist'),
    path('bannercreate', views.bannercreate.as_view(), name='bannercreate'),
    path('banneredit/<int:id>', views.bannercreate.as_view(), name='banneredit'),

    path('countrieslist', views.countrieslist.as_view(), name='countrieslist'),
    path('countriescreate', views.countriescreate.as_view(), name='countriescreate'),
    path('countriesedit/<int:id>', views.countriescreate.as_view(), name='countriesedit'),

    path('patrnerslist', views.patrnerslist.as_view(), name='patrnerslist'),
    path('partnerscreate', views.partnerscreate.as_view(), name='partnerscreate'),
    path('partnersedit/<int:id>', views.partnerscreate.as_view(), name='partnersedit'),
    
    path('universitylist', views.universitylist.as_view(), name='universitylist'),
    path('universitycreate', views.universitycreate.as_view(), name='universitycreate'),
    path('universityedit/<int:id>', views.universitycreate.as_view(), name='universityedit'),
    
    path('serviceslist', views.serviceslist.as_view(), name='serviceslist'),
    path('servicescreate', views.servicescreate.as_view(), name='servicescreate'),
    path('servicesedit/<int:id>', views.servicescreate.as_view(), name='servicesedit'),

    path('testimonialslist', views.testimonialslist.as_view(), name='testimonialslist'),
    path('testimonialscreate', views.testimonialscreate.as_view(), name='testimonialscreate'),
    path('testimonialsedit/<int:id>', views.testimonialscreate.as_view(), name='testimonialsedit'),

    path('eventslist', views.eventslist.as_view(), name='eventslist'),
    path('eventscreate', views.eventscreate.as_view(), name='eventscreate'),
    path('eventsedit/<int:id>', views.eventscreate.as_view(), name='eventsedit'),

    path('enquierylist', views.enquierylist.as_view(), name='enquierylist'),


    

]