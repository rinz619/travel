from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from superadmin.helper import renderhelper, is_ajax
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
# def custom_404_view(request, exception):
#     return render(request, '404.html', status=404)

# Create your views here.
class index(View):
    def get(self, request):
        context = {}
        if request.user.id:
            return redirect('superadmin:dashboard')
        else:
            return renderhelper(request, 'login', 'login', context)
    
    def post(self, request):
        context = {}
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # return HttpResponse(user)

        if user:
            login(request, user)
            return redirect('superadmin:dashboard')
        else:
            context['username'] = username
            context['password'] = password
            messages.info(request, 'Invalid Username or Password')
            return renderhelper(request, 'login', 'login', context)
        

class Logout(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        return redirect('superadmin:login')
    


class profile(LoginRequiredMixin,View):
    def get(self, request):
        context = {}
        return renderhelper(request, 'login', 'profile',context)

    def post(self, request):
        password_to_check = request.POST['oldpassword']
        newpassword = request.POST['newpassword']
        conpassword = request.POST['conpassword']
        password_matches = check_password(password_to_check, request.user.password)
        if password_matches:
            if newpassword == conpassword:
                user = User.objects.get(id=request.user.id)
                new_password = conpassword  # Replace 'new_password' with the new password
                user.set_password(new_password)
                user.pass_text = conpassword
                user.save()
                messages.info(request, 'Password changed')
                return renderhelper(request, 'login', 'profile')
            else:
                messages.info(request, 'new password not matching')
                context = {'oldpass': password_to_check, 'newpassword': newpassword, 'conpassword': conpassword}
                return renderhelper(request, 'login', 'profile', context)

        else:
            messages.info(request, 'Your old password is incorrect')
            context = {'oldpass': password_to_check,'newpassword':newpassword,'conpassword':conpassword}
            return renderhelper(request, 'login', 'profile', context)


class dashboard(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        context['country'] = Countries.objects.all().count()
        context['university'] = Universities.objects.all().count()
        return renderhelper(request, 'home', 'index', context)
    



# Agents module start
class agentslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = User.objects.filter(user_type=3).order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = User.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                User.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                User.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search)| Q(unique_id__icontains=search)
            conditions &= Q(user_type=3)
            data_list = User.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/agents/agents-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'agents', 'agents-view', context)

class agentscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = User.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'agents', 'agents-create', context)

    def post(self, request, id=None):
        try:
            data = User.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = User()
            data.unique_id = 'AG-'+str(random.randint(11111,99999))
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        attachment = request.FILES.get('attachment')
        if uploaded_file:
            data.image = uploaded_file
        if attachment:
            data.attachement = attachment
        data.user_type = 3
        data.address = request.POST.get('address')
        data.name = request.POST.get('name')
        data.contactperson = request.POST.get('contactperson')
        data.trn = request.POST.get('trn')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.password_text = request.POST.get('password')
        data.set_password(request.POST.get('password'))
        data.save()
        return redirect('superadmin:agentslist')

    # Agents module end






# Banner module start
class bannerlist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Banner.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Banner.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Banner.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Banner.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search)
            data_list = Banner.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/banner/banner-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'banner', 'banner-view', context)

class bannercreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Banner.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'banner', 'banner-create', context)

    def post(self, request, id=None):
        try:
            data = Banner.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Banner()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file
        data.title = request.POST['title']
        data.description = request.POST['description']
        data.save()
        return redirect('superadmin:bannerlist')

    # Banner module end


# Countries module start
class countrieslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Countries.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Countries.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Countries.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Countries.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search) | Q(subtitle__icontains=search)
            data_list = Countries.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/countries/countries-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'countries', 'countries-view', context)

class countriescreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Countries.objects.get(id=id)
            context['faqs'] = Faqs.objects.filter(country=id)
        except:
            context['data'] = None
        return renderhelper(request, 'countries', 'countries-create', context)

    def post(self, request, id=None):
        try:
            data = Countries.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Countries()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file

        uploaded_file_flag = request.FILES.get('flagfile')
        if uploaded_file_flag:
            data.flag = uploaded_file_flag

        data.title = request.POST['title']
        data.subtitle = request.POST['subtitle']
        data.description = request.POST['description']
        data.why = request.POST['why']
        data.eligblity = request.POST.getlist('eligiblity')
        data.save()
        question = request.POST.getlist('question')
        answer = request.POST.getlist('answer')
        Faqs.objects.filter(country=data.id).delete()
        for i in range(0,len(question)):
            Faqs(country=data,title=question[i],subtitle=answer[i]).save()
        return redirect('superadmin:countrieslist')

    # Countries module end

# Partners module start
class patrnerslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Partners.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Partners.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Partners.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Partners.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search) | Q(subtitle__icontains=search)
            data_list = Partners.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/partners/partner-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'partners', 'partner-view', context)

class partnerscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Partners.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'partners', 'partner-create', context)

    def post(self, request, id=None):
        try:
            data = Partners.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Partners()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file


        data.save()
        return redirect('superadmin:patrnerslist')

    # Banner module end

# University module start
class universitylist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Universities.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Universities.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Universities.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Universities.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search) | Q(country__title__icontains=search)
            data_list = Universities.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/university/university-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'university', 'university-view', context)

class universitycreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Universities.objects.get(id=id)
        except:
            context['data'] = None
        context['countries'] = Countries.objects.filter(is_active=True)
        return renderhelper(request, 'university', 'university-create', context)

    def post(self, request, id=None):
        try:
            data = Universities.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Universities()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file
        data.country_id = request.POST.get('country')
        data.title = request.POST.get('title')
        data.duration = request.POST.get('duration')
        data.ranking = request.POST.get('ranking')
        data.indian = request.POST.get('indian')
        data.description = request.POST.get('description')
        data.save()
        return redirect('superadmin:universitylist')

    # University module end

# Service module start
class serviceslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Services.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Services.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Services.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Services.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search)
            data_list = Services.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/services/services-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'services', 'services-view', context)

class servicescreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Services.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'services', 'services-create', context)

    def post(self, request, id=None):
        try:
            data = Services.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Services()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file
        data.title = request.POST.get('title')

        data.save()
        return redirect('superadmin:serviceslist')

    # Banner module end

# Testimonials module start
class testimonialslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Testimonials.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Testimonials.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Testimonials.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Testimonials.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search)
            data_list = Testimonials.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/testimonials/testimonials-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'testimonials', 'testimonials-view', context)

class testimonialscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Testimonials.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'testimonials', 'testimonials-create', context)

    def post(self, request, id=None):
        try:
            data = Testimonials.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Testimonials()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file
        data.title = request.POST.get('title')
        data.link = request.POST.get('link')
        data.description = request.POST.get('description')

        data.save()
        return redirect('superadmin:testimonialslist')

    # Testimonials module end

# Events module start
class eventslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Events.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Events.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Events.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Events.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(title__icontains=search)
            data_list = Events.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/events/events-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'events', 'events-view', context)

class eventscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Events.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'events', 'events-create', context)

    def post(self, request, id=None):
        try:
            data = Events.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Events()
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file
        data.title = request.POST.get('title')
        data.start = request.POST.get('startdate')
        data.end = request.POST.get('enddate')

        data.save()
        return redirect('superadmin:eventslist')

    # Testimonials module end

from django.conf import settings
import os


class LogPageView(View):
    def get(self, request):
        context={}
        # Use BASE_DIR from settings to construct the path
        log_file_path = os.path.join(settings.BASE_DIR, 'django_debug.log')
 
        try:
            with open(log_file_path, 'r') as log_file:
                # Read the file content and split into lines
                log_lines = log_file.readlines()
                # Reverse the lines for descending order
                log_lines.reverse()
                # Join the lines back
                log_content = ''.join(log_lines)
        except FileNotFoundError:
            log_content = "Log file not found."
        except Exception as e:
            log_content = f"An error occurred while reading the log file: {e}"
        context['log_content']=log_content
        return renderhelper(request,'log','log',context)
    



# Events module start
class enquierylist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Enquiries.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Enquiries.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Enquiries.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Enquiries.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(name__icontains=search) |  Q(phone__icontains=search) |  Q(email__icontains=search) |  Q(university__icontains=search) 
            data_list = Enquiries.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/enquires/enquiry-table.html')
            html_content = template.render(context, request)
            return JsonResponse({'status': True, 'template': html_content})

       
        p = Paginator(data, 20)
        page_num = request.GET.get('page', 1)
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)
        context['datas'] = page
        context['page'] = page_num

        return renderhelper(request, 'enquires', 'enquiry-view', context)
