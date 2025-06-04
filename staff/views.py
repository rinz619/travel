from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from staff.helper import renderhelper, is_ajax
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from superadmin.models import *
from superadmin.custom_permision import LoginRequiredMixin
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
import random
from datetime import datetime
# Create your views here.




import socket
from django.http import HttpResponse

def get_wifi_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This does NOT send any actual data; just used to determine IP
        s.connect(("8.8.8.8", 80))  # Google's public DNS
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def show_wifi_ip(request):
    ip = get_wifi_ip()  # Do NOT pass `request` here
    return HttpResponse(f"Your Wi-Fi IP is: {ip}")



class index(View):
    
    def get(self, request):
        context = {}
        ip = get_wifi_ip()
        if ip == '192.168.18.85':
            return renderhelper(request, 'login', 'login', context)
        else:
            return renderhelper(request, 'login', 'error', context)
        
    def post(self, request):
        context = {}

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Staffs.objects.get(unique_id=username,password=password)
            if user:
                request.session['userid'] = user.id
        except:
            context['username'] = username
            context['password'] = password
            messages.info(request, 'Invalid Username or Password')
            return renderhelper(request, 'login', 'login', context)
        return redirect('staff:home')
        
    
class home(View):
    def get(self, request):
        context = {}
        if 'userid' in request.session:
            user = Staffs.objects.get(id=request.session['userid'])
            context['user'] = user
            last_login = StaffLogins.objects.filter(staff=user.id,is_absent=False,date=datetime.today()).order_by('id').last()
            context['last_login'] = None
            if last_login:
                lastlogin = StaffTimings.objects.filter(staff=last_login.id,outtime=None).order_by('id').last()
                context['last_login'] = None
                if lastlogin:
                    context['last_login'] = lastlogin
            isabsent = StaffLogins.objects.filter(staff=user.id,is_absent=True,date=datetime.now().date()).last()
            context['is_absent'] = False
            if isabsent:
                context['is_absent'] = True
            
        else:
            return redirect('staff:login')
        return renderhelper(request, 'home', 'index', context)        
    

    
def add_to_login(request):
    userid = request.GET.get('id')

    if int(userid) == int(request.session['userid']):
        current_time_str = datetime.now().strftime("%I:%M %p")
        try:
            data = StaffLogins.objects.get(staff=userid,date=datetime.today())
        except:    
            data = StaffLogins(staff_id=userid,date=datetime.today())
            data.save()
            
        StaffTimings(staff=data,intime=current_time_str).save()
            
        return JsonResponse({'status':True})
    else:
        return JsonResponse({'status':False})
    
    
def add_to_logout(request):
    id = request.GET.get('id')
    staff = StaffTimings.objects.get(id=id)
    if int(staff.staff.staff.id) == int(request.session['userid']):
        current_time_str = datetime.now().strftime("%I:%M %p")
        staff.outtime = current_time_str
        staff.save()
        return JsonResponse({'status':True})
    else:
        return JsonResponse({'status':False})
    
    
class applyleave(View):
    def post(self, request):
        context = {}
        
        approvedby = request.POST.get('approved')
        remarks = request.POST.get('reason')
        
        StaffLogins(staff_id=request.session['userid'],remarks=remarks,is_absent=True,approvedby=approvedby).save()
        
        return redirect('staff:home')
