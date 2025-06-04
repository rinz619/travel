# import firebase_admin
# from firebase_admin import credentials, messaging

# cred = credentials.Certificate("adhoc/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

from django.shortcuts import render
from django.shortcuts import HttpResponse
import datetime
def renderhelper(request,folder,htmlpage,context={}):
    return render(request,'staff/'+folder+'/'+htmlpage+'.html',context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# def sendQAPushNotification(data, name):
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=data['title'],
#             body=data['body'],
#         ),
#         token=data['fcm'],
#     )

#     response = messaging.send(message)
#     return response
#     print('Successfully sent message:', response)

