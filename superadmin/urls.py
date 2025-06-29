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
    path('download_entries_pdf', views.download_entries_pdf, name='download_entries_pdf'),

    path('fileuploads', views.fileuploads.as_view(), name='fileuploads'),

    path('agentslist', views.agentslist.as_view(), name='agentslist'),
    path('agentscreate', views.agentscreate.as_view(), name='agentscreate'),
    path('agentsedit/<int:id>', views.agentscreate.as_view(), name='agentsedit'),

    path('offlinebookingslist', views.offlinebookingslist.as_view(), name='offlinebookingslist'),
    path('offlinebookingscreate', views.offlinebookingscreate.as_view(), name='offlinebookingscreate'),
    path('offlinebookingsedit/<int:id>', views.offlinebookingscreate.as_view(), name='offlinebookingsedit'),
    
    path('cashrecieptlist', views.cashrecieptlist.as_view(), name='cashrecieptlist'),
    path('cashrecieptcreate', views.cashrecieptcreate.as_view(), name='cashrecieptcreate'),
    path('cashrecieptedit/<int:id>', views.cashrecieptcreate.as_view(), name='cashrecieptedit'),

    path('accountledger', views.accountledger.as_view(), name='accountledger'),
    path('download-excel/', views.download_excel, name='download_excel'),
    # path('download-pdf/', views.download_pdf, name='download_pdf'),
    
    path('invoice/<str:id>', views.invoice.as_view(), name='invoice'),
    path('receipt/<str:id>', views.receipt.as_view(), name='receipt'),
    
    path('refund/<str:id>', views.refund.as_view(), name='refund'),
    path('refundlist', views.refundlist.as_view(), name='refundlist'),
    path('refundedit/<str:id>', views.refund.as_view(), name='refundedit'),
    
    path('stafflist', views.stafflist.as_view(), name='stafflist'),
    path('staffcreate', views.staffcreate.as_view(), name='staffcreate'),
    path('staffedit/<int:id>', views.staffcreate.as_view(), name='staffedit'),
    
    path('attendancereport', views.attendancereport.as_view(), name='attendancereport'),

        
    path('walletslist', views.walletslist.as_view(), name='walletslist'),
    path('walletscreate', views.walletscreate.as_view(), name='walletscreate'),
    path('walletsedit/<int:id>', views.walletscreate.as_view(), name='walletsedit'),
    
        
    path('leadslist', views.leadslist.as_view(), name='leadslist'),
    path('leadscreate', views.leadscreate.as_view(), name='leadscreate'),
    path('leadsedit/<int:id>', views.leadscreate.as_view(), name='leadsedit'),
    path('leaddetail/<int:id>', views.leaddetail.as_view(), name='leaddetail'),
    

        
    path('subadminslist', views.subadminslist.as_view(), name='subadminslist'),
    path('subadmincreate', views.subadmincreate.as_view(), name='subadmincreate'),
    path('subadminedit/<int:id>', views.subadmincreate.as_view(), name='subadminedit'),
    
    
    
    path('salesreport', views.salesreport.as_view(), name='salesreport'),
    path('salesreportcreate', views.salesreportcreate.as_view(), name='salesreportcreate'),
    path('salesreportedit/<int:id>', views.salesreportcreate.as_view(), name='salesreportedit'),
    
    path('cashreciept', views.cashreciept.as_view(), name='cashreciept'),
    path('salsecashrecieptcreate', views.salescashrecieptcreate.as_view(), name='salsecashrecieptcreate'),
    path('salscashrecieptedit/<int:id>', views.cashrecieptcreate.as_view(), name='salscashrecieptedit'),



    
    path('bannerlogincreate', views.bannerlogincreate.as_view(), name='bannerlogincreate'),





    

]