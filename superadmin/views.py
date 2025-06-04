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
from datetime import datetime
# def custom_404_view(request, exception):
#     return render(request, '404.html', status=404)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from num2words import num2words
import openpyxl



def check_previllage(request,menu):
    if request.user.user_type == 1:
        return True
    else:
    
        ismenu = Previllages.objects.filter(user=request.user.id,option=menu).first()
        if ismenu:
            return ismenu
        else:
            return None
    
        
    
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
        clientid = request.POST.get('clientid')
        try:
            user = User.objects.get(email=username, password=password, unique_id=clientid, user_type=3)
            print('user===',user)
        except Exception as e:
            print('error====',e)
            try:
                user = User.objects.get(email=username, password=password, user_type=1)
                print('user===',user)
            except:
                user = None

        user = authenticate(username=username, password=password)

        if user:
            if user.user_type == 1:
                login(request, user)
                return redirect('superadmin:dashboard')
            elif user.user_type != 1 and user.unique_id == clientid:
                login(request, user)
                return redirect('superadmin:dashboard')
            else:
                context['username'] = username
                context['password'] = password
                context['clientid'] = clientid
                messages.info(request, 'Invalid Credentials')
                return renderhelper(request, 'login', 'login', context)
            
        else:
            context['username'] = username
            context['password'] = password
            context['clientid'] = clientid
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
                conditions &= Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(contactperson__icontains=search) | Q(trn__icontains=search)| Q(address__icontains=search)
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
        data.agenttype = request.POST.get('agenttype')
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



# Bookings module start

class offlinebookingslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Bookings.objects.filter(is_delete=False).order_by('-id')
        context['range'] = range(1,len(data)+1)
        context['previllage'] = check_previllage(request, 'Offline Bookings')
        context['agents'] = User.objects.filter(user_type=3,is_active=True).order_by('name')
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            agent = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Bookings.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Bookings.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Bookings.objects.filter(id=id).update(is_delete=True)
                messages.info(request, 'Successfully Deleted')
            if agent:
                conditions &= Q(agent=agent)
            if search:
                conditions &= Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(contactperson__icontains=search) | Q(trn__icontains=search)| Q(address__icontains=search)
            conditions &= Q(is_delete=False)
            data_list = Bookings.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/bookings/bookings-table.html')
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

        return renderhelper(request, 'bookings', 'bookings-view', context)

class offlinebookingscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Bookings.objects.get(id=id)
        except:
            context['data'] = None
        context['agents'] = User.objects.filter(user_type=3,is_active=True).order_by('name')
        context['airports'] = Airports.objects.all().order_by('city_airport')
        context['airlines'] = Airlines.objects.all().order_by('name')
        return renderhelper(request, 'bookings', 'bookings-create', context)

    def post(self, request, id=None):
        try:
            data = Bookings.objects.get(id=id)
            data.createdby = request.user
            account = AccountLedgers.objects.get(unique_id=data.unique_id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"TBTINV{year_month}"

            # Filter and find max matching unique_id starting with this prefix
            latest = Bookings.objects.filter(unique_id__startswith=prefix).aggregate(Max('unique_id'))['unique_id__max']

            if latest:
                # Extract the numeric suffix from the end
                last_seq = int(latest[len(prefix):])
                next_seq = last_seq + 1
            else:
                next_seq = 1
        
        
            # now = datetime.now()
            # year_month_format = f"{now.year % 100:02d}{now.month:02d}"
            agent = request.POST.get('agent')
            balance = AccountLedgers.objects.filter(agent=agent).order_by('-id').first().balance
            if not balance:
                balance = 0
            account = AccountLedgers()
            data = Bookings()
            data.unique_id = f"{prefix}{next_seq}"
            data.createdby = request.user
            account.unique_id = f"{prefix}{next_seq}"

            messages.info(request, 'Successfully Added')


        data.agent_id = request.POST.get('agent')
        data.servicetype = request.POST.get('servicetype')
        data.fromairport = request.POST.get('fromairport')
        data.toairport = request.POST.get('toairport')
        departuredate = request.POST.get('departuredate')
        if departuredate:
            data.departuredate = departuredate
        else:
            data.departuredate = None
        data.airline = request.POST.get('airline')
        data.pnr = request.POST.get('pnr')
        data.passportnumber = request.POST.get('passportnumber')
        data.ticketnumber = request.POST.get('ticketnumber')
        data.passengername = request.POST.get('passengername')
        data.servicedescription = request.POST.get('servicedescription')
        data.netamount = request.POST.get('netamount')
        data.grossamount = request.POST.get('grossamount')
        data.markup = request.POST.get('markup')
        data.remarks = request.POST.get('remarks')
        data.save()
        
        account.agent_id = request.POST.get('agent')
        account.pnr = request.POST.get('pnr')
        account.transactiontype = 'Offline Booking'
        account.date = datetime.now().date()
        account.debit = request.POST.get('grossamount')
        account.balance = float(balance) - float(request.POST.get('grossamount'))
        account.save()
        return redirect('superadmin:offlinebookingslist')

    # Agents module end


# Bookings module start

class cashrecieptlist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = CashReceipts.objects.filter(is_delete=False).order_by('-id')
        context['range'] = range(1,len(data)+1)
        context['previllage'] = check_previllage(request, 'Accounts')
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = CashReceipts.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                CashReceipts.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                CashReceipts.objects.filter(id=id).update(is_delete=True)
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(receivedfrom__icontains=search) | Q(paymenttype__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(agent__name__icontains=search) 
            
            conditions &= Q(is_delete=False)
            data_list = CashReceipts.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/cash/cash-table.html')
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

        return renderhelper(request, 'cash', 'cash-view', context)

class cashrecieptcreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = CashReceipts.objects.get(id=id)
        except:
            context['data'] = None
        context['agents'] = User.objects.filter(user_type=3,is_active=True).order_by('name')
        context['airports'] = Airports.objects.all().order_by('city_airport')
        context['airlines'] = Airlines.objects.all().order_by('name')
        return renderhelper(request, 'cash', 'cash-create', context)

    def post(self, request, id=None):
        try:
            data = CashReceipts.objects.get(id=id)
            account = AccountLedgers.objects.get(unique_id=data.unique_id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"REC{year_month}"

            # Filter and find max matching unique_id starting with this prefix
            latest = CashReceipts.objects.filter(unique_id__startswith=prefix).aggregate(Max('unique_id'))['unique_id__max']

            if latest:
                # Extract the numeric suffix from the end
                last_seq = int(latest[len(prefix):])
                next_seq = last_seq + 1
            else:
                next_seq = 1
        
        
            # now = datetime.now()
            # year_month_format = f"{now.year % 100:02d}{now.month:02d}"
            account = AccountLedgers()
            data = CashReceipts()
            data.unique_id = f"{prefix}{next_seq}"
            account.unique_id = f"{prefix}{next_seq}"

            messages.info(request, 'Successfully Added')


        data.agent_id = request.POST.get('agent')
        data.paymenttype = request.POST.get('paymenttype')
        data.receivedfrom = request.POST.get('receivedfrom')
        data.phone = request.POST.get('phone')
        data.amount = request.POST.get('amount')
        data.description = request.POST.get('description')
        
        data.save()
        
        account.agent_id = request.POST.get('agent')
        account.transactiontype = 'Cash'
        account.date = datetime.now().date()
        account.credit = request.POST.get('amount')
        account.save()
        return redirect('superadmin:cashrecieptlist')

    # Agents module end




# accountledger module start
class accountledger(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        if request.user.user_type == 3:
            data = AccountLedgers.objects.filter(agent=request.user.id).order_by('-id')
        else:    
            data = AccountLedgers.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            fromdate = request.GET.get('fromdate')
            todate = request.GET.get('todate')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = AccountLedgers.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                AccountLedgers.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                AccountLedgers.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if fromdate:
                conditions &= Q(date__gte=fromdate)
            if todate:
                conditions &= Q(date__lte=todate)
                
            if request.user.user_type == 3:
                conditions &= Q(agent=request.user.id)
                    
                
            data_list = AccountLedgers.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/ledger/ledger-table.html')
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

        return renderhelper(request, 'ledger', 'ledger-view', context)


class invoice(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] =data= Bookings.objects.get(unique_id=id)
            num = data.grossamount
            context['num_in_words'] = num2words(num, to='cardinal', lang='en').title() + ' AED Only '
        except:
            context['data'] = None
        return renderhelper(request, 'invoice', 'invoice', context)

class receipt(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] =data= CashReceipts.objects.get(unique_id=id)
            num = data.amount
            context['num_in_words'] = num2words(num, to='cardinal', lang='en').title() + ' AED Only '
        except:
            context['data'] = None
        return renderhelper(request, 'invoice', 'receipt', context)




# Bookings module start

class refundlist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Refunds.objects.filter(is_delete=False).order_by('-id')
        context['range'] = range(1,len(data)+1)
        context['previllage'] = check_previllage(request, 'Bookings')
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = Refunds.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                wallet = Refunds.objects.get(id=id)
                wallet.is_verify=True
                wallet.save()
                print('wallet===',wallet.booking)
                user = User.objects.get(id=wallet.booking.agent.id)
                wallet_balance = user.wallet
                if wallet_balance:
                    user.wallet = wallet_balance + wallet.refundamount
                else:
                    user.wallet =   wallet.refundamount

                user.save()
                balance = AccountLedgers.objects.filter(agent=wallet.booking.agent.id).order_by('-id').first().balance
                if not balance:
                    balance = 0
                    
                acc = AccountLedgers()
                acc.agent = wallet.booking.agent
                acc.unique_id = wallet.unique_id
                acc.transactiontype = 'CREDIT NOTE'
                acc.pnr = wallet.booking.pnr
                acc.date = datetime.now().date()
                acc.credit = wallet.refundamount
                acc.balance = balance + wallet.refundamount
                acc.save()
                messages.info(request, 'Successfully Verified')
                
            elif type == '2':
                id = request.GET.get('id')
                Refunds.objects.filter(id=id).update(is_delete=True)
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(receivedfrom__icontains=search) | Q(paymenttype__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(agent__name__icontains=search) 
            conditions &= Q(is_delete=False)
            data_list = Refunds.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/refund/refund-table.html')
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

        return renderhelper(request, 'refund', 'refund-view', context)


class refund(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] =data= Bookings.objects.get(unique_id=id)            
        except:
            context['data'] = Refunds.objects.get(id=int(id))   
            
        return renderhelper(request, 'refund', 'refund-create', context)
    def post(self, request, id=None):
        try:
            data = Refunds.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"TBTCN{year_month}"

            # Filter and find max matching unique_id starting with this prefix
            latest = Refunds.objects.filter(unique_id__startswith=prefix).aggregate(Max('unique_id'))['unique_id__max']

            if latest:
                # Extract the numeric suffix from the end
                last_seq = int(latest[len(prefix):])
                next_seq = last_seq + 1
            else:
                next_seq = 1
                
            data = Refunds()
            data.booking = Bookings.objects.get(unique_id=id)  
            data.unique_id =  f"{prefix}{next_seq}"
            messages.info(request, 'Successfully Added')

        
        
        data.netamount = request.POST.get('netamount')
        data.grossamount = request.POST.get('grossamount')
        data.markup = request.POST.get('markup')
        data.remarks = request.POST.get('remarks')
        data.refundamount = request.POST.get('refundamount')
        data.save()
        return redirect('superadmin:refundlist')




def download_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Transactions'

    headers = ["Sl No", "Invoice No", "Transaction Date", "Transaction Type", "PNR", "Sector", "Description", "Debit", "Credit", "Running Balance"]
    sheet.append(headers)

    datas = AccountLedgers.objects.all()
    for idx, i in enumerate(datas, start=1):
        sheet.append([
            idx,
            i.unique_id,
            i.date.strftime("%Y-%m-%d") if i.date else '',
            i.transactiontype,
            '', '', '',  # Fill PNR, Sector, Description if you have them
            i.debit if i.debit else '-',
            i.credit if i.credit else '-',
            i.balance if i.balance else '0.00'
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=transactions.xlsx'
    workbook.save(response)
    return response


import pandas as pd


class fileuploads(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        return renderhelper(request, 'file', 'file', context)
    def post(self, request):
        file_path = request.FILES.get('myfile')
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            Airlines.objects.create(
            iata=row['IATA'],
            name=row['Airline'],
            country_or_region=row['Country/Region']
            )
        print(file_path)
        return HttpResponse('in')

# from django.template.loader import get_template
# from xhtml2pdf import pisa
# from django.http import HttpResponse

# def download_pdf(request):
#     datas = AccountLedgers.objects.all()  # or filtered data
#     template = get_template('your_app/pdf_template.html')  # adjust path
#     html = template.render({'datas': datas})
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
#     pisa_status = pisa.CreatePDF(html, dest=response)
#     if pisa_status.err:
#         return HttpResponse("Error generating PDF", status=500)
#     return response





# Staff module start
class stafflist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Staffs.objects.all().order_by('-id')
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
                cat = Staffs.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                Staffs.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Staffs.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(emergency__icontains=search) | Q(passportno__icontains=search)| Q(address__icontains=search)
            data_list = Staffs.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/staff/staff-table.html')
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

        return renderhelper(request, 'staff', 'staff-view', context)

class staffcreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Staffs.objects.get(id=id)
        except:
            context['data'] = None
        return renderhelper(request, 'staff', 'staff-create', context)

    def post(self, request, id=None):
        try:
            data = Staffs.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Staffs()
            data.unique_id = 'ST-'+str(random.randint(11111,99999))
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        if uploaded_file:
            data.image = uploaded_file

        data.address = request.POST.get('address')
        data.name = request.POST.get('name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.passportno = request.POST.get('passportno')
        data.emergency = request.POST.get('emergency')
        data.save()
        return redirect('superadmin:stafflist')

    # Agents module end




# Staff module start
class walletslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        if request.user.user_type == 3:
            data = WalletUPdates.objects.filter(agent=request.user.id).order_by('-id')
        else:
            data = WalletUPdates.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        context['previllage'] = check_previllage(request, 'Accounts')
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = WalletUPdates.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                wallet = WalletUPdates.objects.get(id=id)
                wallet.is_verify=True
                wallet.save()
                
                user = User.objects.get(id=wallet.agent.id)
                wallet_balance = user.wallet
                if wallet_balance:
                    user.wallet = wallet_balance + wallet.amount
                else:
                    user.wallet =   wallet.amount

                user.save()
                balance = AccountLedgers.objects.filter(agent=wallet.agent.id).order_by('-id').first().balance
                if not balance:
                    balance = 0
                    
                acc = AccountLedgers()
                acc.agent = wallet.agent
                acc.unique_id = 'INV6669'
                acc.credit = wallet.amount
                acc.balance = balance + wallet.amount
                acc.save()
                messages.info(request, 'Successfully Verified')
            elif type == '2':
                id = request.GET.get('id')
                WalletUPdates.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(agent__name__icontains=search) | Q(transactiontype__icontains=search) | Q(referencenumber__icontains=search) | Q(transactiondate__icontains=search)| Q(amount__icontains=search) 
            if request.user.user_type == 3:
                conditions &= Q(agent=request.user.id)            
            data_list = WalletUPdates.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/wallet/wallet-table.html')
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

        return renderhelper(request, 'wallet', 'wallet-view', context)

class walletscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = WalletUPdates.objects.get(id=id)
        except:
            context['data'] = None
        context['agents'] = User.objects.filter(user_type=3,is_active=True).order_by('name')

        return renderhelper(request, 'wallet', 'wallet-create', context)

    def post(self, request, id=None):
        try:
            data = WalletUPdates.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = WalletUPdates()
            data.unique_id = 'ST-'+str(random.randint(11111,99999))
            messages.info(request, 'Successfully Added')

        attachment = request.FILES.get('attachment')
        if attachment:
            data.attachment = attachment
        if request.user.user_type == 3:
            data.agent = request.user
        else:    
            data.agent_id = request.POST.get('agent')
        data.transactiontype = request.POST.get('transactiontype')
        data.transactiondate = request.POST.get('transactiondate')
        data.amount = request.POST.get('amount')
        data.referencenumber = request.POST.get('referencenumber')
        data.bankdetails = request.POST.get('bankdetails')
        data.save()
        
        
        return redirect('superadmin:walletslist')

    # Agents module end


# Staff module start
class leadslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = Leads.objects.all().order_by('-id')
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
                cat = Leads.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                Leads.objects.filter(id=id).update(is_verify=True)
                messages.info(request, 'Successfully Verified')
            elif type == '2':
                id = request.GET.get('id')
                Leads.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(agent__name__icontains=search) | Q(transactiontype__icontains=search) | Q(referencenumber__icontains=search) | Q(transactiondate__icontains=search)| Q(amount__icontains=search) 
            data_list = Leads.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/leads/leads-table.html')
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

        return renderhelper(request, 'leads', 'leads-view', context)



class leaddetail(LoginRequiredMixin, View):
    def post(self, request, id=None):
        
        data = LeadsDetails()
        data.lead_id = id
        data.status = request.POST.get('status')
        data.remarks = request.POST.get('remarks')
        data.save()
        
        return redirect('superadmin:leaddetail',id=id)
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Leads.objects.get(id=id)
        except:
            context['data'] = None
        context['remarks'] = LeadsDetails.objects.filter(lead=id).order_by('id')

        return renderhelper(request, 'leads', 'lead-detail', context)

class leadscreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Leads.objects.get(id=id)
        except:
            context['data'] = None
        context['staffs'] = Staffs.objects.filter(is_active=True).order_by('name')

        return renderhelper(request, 'leads', 'leads-create', context)

    def post(self, request, id=None):
        try:
            data = Leads.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = Leads()
            data.unique_id = 'ST-'+str(random.randint(11111,99999))
            messages.info(request, 'Successfully Added')

        attachment = request.FILES.get('attachment')
        if attachment:
            data.attachment = attachment

        data.staff_id = request.POST.get('staff')
        data.leadsource = request.POST.get('leadsource')
        data.clientname = request.POST.get('clientname')
        data.phone = request.POST.get('phone')
        data.enquiry = request.POST.get('enquiry')
        data.description = request.POST.get('description')
        data.save()
        
        
        return redirect('superadmin:leadslist')

    # Agents module end


# Staff module start
class subadminslist(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = User.objects.filter(user_type=2).order_by('-id')
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
                User.objects.filter(id=id).update(is_verify=True)
                messages.info(request, 'Successfully Verified')
            elif type == '2':
                id = request.GET.get('id')
                User.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            conditions &= Q(user_type=2)
            if search:
                conditions &= Q(agent__name__icontains=search) | Q(transactiontype__icontains=search) | Q(referencenumber__icontains=search) | Q(transactiondate__icontains=search)| Q(amount__icontains=search) 
            data_list = User.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/subadmin/subadmin-table.html')
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

        return renderhelper(request, 'subadmin', 'subadmin-view', context)



class subadmincreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = User.objects.get(id=id)
            context['pre_data'] = Previllages.objects.filter(user=id)
        except:
            context['data'] = None
            context['pre_data'] = None
        context['staffs'] = Staffs.objects.filter(is_active=True).order_by('name')

        return renderhelper(request, 'subadmin', 'subadmin-create', context)

    def post(self, request, id=None):
        try:
            data = User.objects.get(id=id)
            messages.info(request, 'Successfully Updated')
        except:
            data = User()
            
            data.unique_id = 'SA-'+str(random.randint(11111,99999))
            messages.info(request, 'Successfully Added')

        uploaded_file = request.FILES.get('imagefile')
        attachment = request.FILES.get('attachment')
        if uploaded_file:
            data.image = uploaded_file
        if attachment:
            data.attachement = attachment
        data.user_type = 2
        data.address = request.POST.get('address')
        data.name = request.POST.get('name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.password_text = request.POST.get('password')
        data.set_password(request.POST.get('password'))
        data.save()
        
        Previllages.objects.filter(user=data.id).delete()
        # Agents
        agent_read = request.POST.get('agent_read')
        agent_write = request.POST.get('agent_write')
        agent_delete = request.POST.get('agent_delete')
        
        sub = Previllages()
        sub.user = data
        sub.option = 'Agent'
        if agent_read:
            sub.read = True
        if agent_write:
            sub.write = True
        if agent_delete:
            sub.delete = True
        sub.save()

        # Subadmin
        subadmin_read = request.POST.get('subadmin_read')
        subadmin_write = request.POST.get('subadmin_write')
        subadmin_delete = request.POST.get('subadmin_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Subadmin'
        if subadmin_read:
            sub.read = True
        if subadmin_write:
            sub.write = True
        if subadmin_delete:
            sub.delete = True
        sub.save()

        # Offline Bookings
        booking_read = request.POST.get('booking_read')
        booking_write = request.POST.get('booking_write')
        booking_delete = request.POST.get('booking_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Offline Bookings'
        if booking_read:
            sub.read = True
        if booking_write:
            sub.write = True
        if booking_delete:
            sub.delete = True
        sub.save()

        # Refunds
        refunds_read = request.POST.get('refunds_read')
        refunds_write = request.POST.get('refunds_write')
        refunds_delete = request.POST.get('refunds_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Refunds'
        if refunds_read:
            sub.read = True
        if refunds_write:
            sub.write = True
        if refunds_delete:
            sub.delete = True
        sub.save()

        # Cash Receipt
        cash_read = request.POST.get('cash_read')
        cash_write = request.POST.get('cash_write')
        cash_delete = request.POST.get('cash_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Cash Receipt'
        if cash_read:
            sub.read = True
        if cash_write:
            sub.write = True
        if cash_delete:
            sub.delete = True
        sub.save()

        # Account Ledger
        ledger_read = request.POST.get('ledger_read')
        ledger_write = request.POST.get('ledger_write')
        ledger_delete = request.POST.get('ledger_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Account Ledger'
        if ledger_read:
            sub.read = True
        if ledger_write:
            sub.write = True
        if ledger_delete:
            sub.delete = True
        sub.save()

        # Update Wallet
        wallet_read = request.POST.get('wallet_read')
        wallet_write = request.POST.get('wallet_write')
        wallet_delete = request.POST.get('wallet_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Update Wallet'
        if wallet_read:
            sub.read = True
        if wallet_write:
            sub.write = True
        if wallet_delete:
            sub.delete = True
        sub.save()

        # Sales Report
        sales_read = request.POST.get('sales_read')
        sales_write = request.POST.get('sales_write')
        sales_delete = request.POST.get('sales_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Sales Report'
        if sales_read:
            sub.read = True
        if sales_write:
            sub.write = True
        if sales_delete:
            sub.delete = True
        sub.save()

        # Leads
        leads_read = request.POST.get('leads_read')
        leads_write = request.POST.get('leads_write')
        leads_delete = request.POST.get('leads_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Leads'
        if leads_read:
            sub.read = True
        if leads_write:
            sub.write = True
        if leads_delete:
            sub.delete = True
        sub.save()

        # Attendance Report
        attendance_read = request.POST.get('attendance_read')
        attendance_write = request.POST.get('attendance_write')
        attendance_delete = request.POST.get('attendance_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Attendance report'
        if attendance_read:
            sub.read = True
        if attendance_write:
            sub.write = True
        if attendance_delete:
            sub.delete = True
        sub.save()

        # Staff
        staff_read = request.POST.get('staff_read')
        staff_write = request.POST.get('staff_write')
        staff_delete = request.POST.get('staff_delete')

        sub = Previllages()
        sub.user = data
        sub.option = 'Staff'
        if staff_read:
            sub.read = True
        if staff_write:
            sub.write = True
        if staff_delete:
            sub.delete = True
        sub.save()

        
        return redirect('superadmin:subadminslist')

    # Agents module end





# Bookings module start

class salesreport(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = SalesLedger.objects.all().order_by('-id')
        context['range'] = range(1,len(data)+1)
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            fromdate = request.GET.get('fromdate')
            todate = request.GET.get('todate')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = SalesLedger.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                SalesLedger.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                SalesLedger.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if fromdate:
                conditions &= Q(date__gte=fromdate)
            if todate:
                conditions &= Q(date__lte=todate)
                
            if request.user.user_type == 3:
                conditions &= Q(agent=request.user.id)
                    
                
            data_list = SalesLedger.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/ledger/ledger-table.html')
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

        return renderhelper(request, 'sales', 'ledger-view', context)

class salesreportcreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = Sales.objects.get(id=id)
        except:
            context['data'] = None
        context['agents'] = User.objects.filter(user_type=3,is_active=True).order_by('name')
        context['airports'] = Airports.objects.all().order_by('city_airport')
        context['airlines'] = Airlines.objects.all().order_by('name')
        return renderhelper(request, 'sales', 'sales-create', context)

    def post(self, request, id=None):
        try:
            data = Sales.objects.get(id=id)
            data.createdby = request.user
            account = SalesLedger.objects.get(unique_id=data.unique_id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"TBTINV{year_month}"

            # Filter and find max matching unique_id starting with this prefix
            latest = Sales.objects.filter(unique_id__startswith=prefix).aggregate(Max('unique_id'))['unique_id__max']

            if latest:
                # Extract the numeric suffix from the end
                last_seq = int(latest[len(prefix):])
                next_seq = last_seq + 1
            else:
                next_seq = 1

  
            account = SalesLedger()
            data = Sales()
            data.unique_id = f"{prefix}{next_seq}"
            data.createdby = request.user
            account.unique_id = f"{prefix}{next_seq}"

            messages.info(request, 'Successfully Added')


        data.servicetype = request.POST.get('servicetype')
        data.fromairport = request.POST.get('fromairport')
        data.toairport = request.POST.get('toairport')
        departuredate = request.POST.get('departuredate')
        if departuredate:
            data.departuredate = departuredate
        else:
            data.departuredate = None
        data.airline = request.POST.get('airline')
        data.pnr = request.POST.get('pnr')
        data.passportnumber = request.POST.get('passportnumber')
        data.ticketnumber = request.POST.get('ticketnumber')
        data.passengername = request.POST.get('passengername')
        data.servicedescription = request.POST.get('servicedescription')
        data.netamount = request.POST.get('netamount')
        data.grossamount = request.POST.get('grossamount')
        data.markup = request.POST.get('markup')
        data.remarks = request.POST.get('remarks')
        data.save()
        
        account.pnr = request.POST.get('pnr')
        account.transactiontype = 'Offline Booking'
        account.date = datetime.now().date()
        account.debit = request.POST.get('grossamount')
        account.save()
        return redirect('superadmin:salesreport')

    # Agents module end




# Bookings module start

class cashreciept(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        conditions = Q()
        data = SalesCashReceipts.objects.filter(is_delete=False).order_by('-id')
        
        context['range'] = range(1,len(data)+1)
        context['previllage'] = check_previllage(request, 'Accounts')
        if is_ajax(request):
            page = request.GET.get('page', 1)
            context['page'] = page
            status = request.GET.get('status')
            search = request.GET.get('search')
            type = request.GET.get('type')
            if type == '1':
                id = request.GET.get('id')
                vl = request.GET.get('vl')
                cat = SalesCashReceipts.objects.get(id=id)
                if vl == '2':
                    cat.is_active = False
                else:
                    cat.is_active = True
                cat.save()
                messages.info(request, 'Successfully Updated')
            elif type == '4':
                id = request.GET.get('id')
                seq = request.GET.get('seq')
                SalesCashReceipts.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                SalesCashReceipts.objects.filter(id=id).update(is_delete=True)
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(receivedfrom__icontains=search) | Q(paymenttype__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(agent__name__icontains=search) 
            
            conditions &= Q(is_delete=False)
            data_list = SalesCashReceipts.objects.filter(conditions).order_by('-id')
            paginator = Paginator(data_list, 20)

            try:
                datas = paginator.page(page)
            except PageNotAnInteger:
                datas = paginator.page(1)
            except EmptyPage:
                datas = paginator.page(paginator.num_pages)
            context['datas'] = datas
            template = loader.get_template('superadmin/cash/cash-table.html')
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

        return renderhelper(request, 'salescash', 'cash-view', context)

class salescashrecieptcreate(LoginRequiredMixin, View):
    def get(self, request, id=None):
        context = {}
        try:
            context['data'] = SalesCashReceipts.objects.get(id=id)
        except:
            context['data'] = None
        context['airports'] = Airports.objects.all().order_by('city_airport')
        context['airlines'] = Airlines.objects.all().order_by('name')
        allcash = SalesCashReceipts.objects.filter(is_delete=False)
        ids = []
        for i in allcash:
            ids.append(i.sale.id)
        context['sales'] = Sales.objects.filter(is_delete=False).order_by('unique_id').exclude(id__in=ids)
        
        return renderhelper(request, 'salescash', 'cash-create', context)

    def post(self, request, id=None):
        try:
            data = SalesCashReceipts.objects.get(id=id)
            account = SalesLedger.objects.get(unique_id=data.unique_id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"REC{year_month}"

            # Filter and find max matching unique_id starting with this prefix
            latest = SalesCashReceipts.objects.filter(unique_id__startswith=prefix).aggregate(Max('unique_id'))['unique_id__max']

            if latest:
                # Extract the numeric suffix from the end
                last_seq = int(latest[len(prefix):])
                next_seq = last_seq + 1
            else:
                next_seq = 1
        
        
            # now = datetime.now()
            # year_month_format = f"{now.year % 100:02d}{now.month:02d}"
            account = SalesLedger()
            data = SalesCashReceipts()
            data.unique_id = f"{prefix}{next_seq}"
            account.unique_id = f"{prefix}{next_seq}"

            messages.info(request, 'Successfully Added')



        data.sale_id = request.POST.get('salesinvoice')
        data.paymenttype = request.POST.get('paymenttype')
        data.receivedfrom = request.POST.get('receivedfrom')
        data.phone = request.POST.get('phone')
        data.amount = request.POST.get('amount')
        data.description = request.POST.get('description')
        
        data.save()
        
        account.transactiontype = 'Cash'
        account.date = datetime.now().date()
        account.credit = request.POST.get('amount')
        account.save()
        return redirect('superadmin:cashreciept')

    # Agents module end





# myapp/views.py
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
# Import landscape for page orientation and inch for defining precise widths
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
# Import Paragraph for text wrapping and Spacer for adding vertical space
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch # Import inch for unit measurements
from io import BytesIO


def download_entries_pdf(request):
    buffer = BytesIO()
    # Set page size to landscape letter for more horizontal space
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()

    elements = []

    # Title
    title_text = "Booking Entries Report"
    # Use a heading style for the title
    elements.append(Paragraph(title_text, styles['h1']))
    # Add a spacer for better visual separation instead of <br/>
    elements.append(Spacer(1, 0.2 * inch))

    # Fetch data from your model
    # Ensure 'Bookings' model and its fields (passengername, created_at, servicedescription) exist
    entries = Bookings.objects.all().order_by('id')

    # Define a style for paragraph content within table cells.
    # This is crucial for text wrapping and setting a smaller font size.
    cell_paragraph_style = styles['Normal']
    cell_paragraph_style.fontSize = 7 # Smaller font size for cell content
    cell_paragraph_style.leading = 9 # Adjust leading (line spacing) for smaller font

    # Prepare data for the table
    # Update these headers to reflect your actual 10 columns accurately
    data = [
        [
            'Passenger Name', 'Booking ID', 'Created At', 'Service Description',
            'Contact Email', 'Service Type', 'Booking Status', 'Amount',
            'Payment Status', 'Notes'
        ]
    ]

    for entry in entries:
        # Each item in the inner list corresponds to a column.
        # Wrap text in Paragraph objects to enable automatic line breaks within cells.
        # Replace placeholder data with your actual 'entry' object's attributes for all 10 columns.
        data.append([
            Paragraph(str(entry.passengername), cell_paragraph_style),
            Paragraph(str(entry.id), cell_paragraph_style), # Example: using entry.id as a column
            Paragraph(entry.created_at.strftime('%Y-%m-%d %H:%M'), cell_paragraph_style),
            Paragraph(entry.servicedescription if entry.servicedescription else 'N/A', cell_paragraph_style),
            # --- Placeholder for your additional 6 columns ---
            Paragraph('email@example.com', cell_paragraph_style), # Replace with actual email field
            Paragraph('Service Type A', cell_paragraph_style),     # Replace with actual service type field
            Paragraph('Confirmed', cell_paragraph_style),         # Replace with actual status field
            Paragraph('$100.00', cell_paragraph_style),           # Replace with actual amount field
            Paragraph('Paid', cell_paragraph_style),              # Replace with actual payment status field
            Paragraph('Any additional notes here. This is a longer text to demonstrate wrapping within the cell.', cell_paragraph_style) # Replace with actual notes field
        ])

    # Define column widths for 10 columns.
    # Total usable width for landscape letter is approx 10 inches (11 inches page width - 0.5 inch left margin - 0.5 inch right margin).
    # Adjust these widths based on the content of each column.
    # Using 'None' for some columns allows ReportLab to auto-calculate their width based on content,
    # but for 10 columns, a more explicit distribution is often better.
    # Example distribution (totaling approx 10 inches):
    col_widths = [
        1.2 * inch, # Passenger Name
        0.8 * inch, # Booking ID
        1.3 * inch, # Created At
        1.8 * inch, # Service Description (can be longer)
        1.2 * inch, # Contact Email
        1.0 * inch, # Service Type
        1.0 * inch, # Booking Status
        0.8 * inch, # Amount
        1.0 * inch, # Payment Status
        1.5 * inch  # Notes (can be very long, will wrap)
    ]

    # Create the table
    # `repeatRows=1` ensures the header row repeats on each new page
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Apply table style
    table.setStyle(TableStyle([
        # Header row style
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A4A4A')), # Darker grey for header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'), # Center align header text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8), # Slightly larger font for header
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8), # Reduced padding for header

        # Body rows style
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), # White background for body rows
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'), # Left align body text
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4), # Reduced padding for body cells
        ('TOPPADDING', (0, 1), (-1, -1), 4),

        # Grid lines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # Lighter grid lines
        ('BOX', (0, 0), (-1, -1), 1, colors.black), # Outer box border
    ]))

    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="booking_report.pdf"'
    return response
