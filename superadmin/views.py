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
    try:
        previllage = Previllages.objects.get(user=request.user.id, option=menu)
        prev = (previllage.acsess)
        if prev == 'Read':
            return False
        else:
            return True
    except:
        return True
    
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
        data = Bookings.objects.all().order_by('-id')
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
                Bookings.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(contactperson__icontains=search) | Q(trn__icontains=search)| Q(address__icontains=search)
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
            account = AccountLedgers.objects.get(unique_id=data.unique_id)
            messages.info(request, 'Successfully Updated')
        except:
            
            now = datetime.now()
            year_month = f"{now.year % 100:02d}{now.month:02d}"  # e.g., 2505
            prefix = f"INV{year_month}"

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
        data = CashReceipts.objects.all().order_by('-id')
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
                CashReceipts.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(receivedfrom__icontains=search) | Q(paymenttype__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(agent__name__icontains=search) 
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
        data = Refunds.objects.all().order_by('-id')
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
                seq = request.GET.get('seq')
                Refunds.objects.filter(id=id).update(sequence=seq)
                messages.info(request, 'Successfully Updated')
            elif type == '2':
                id = request.GET.get('id')
                Refunds.objects.filter(id=id).delete()
                messages.info(request, 'Successfully Deleted')
            if status:
                conditions &= Q(is_active=status)
            if search:
                conditions &= Q(receivedfrom__icontains=search) | Q(paymenttype__icontains=search) | Q(phone__icontains=search) | Q(unique_id__icontains=search)| Q(agent__name__icontains=search) 
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
            data = Refunds()
            data.booking_unique_id = id
            data.unique_id = id
            messages.info(request, 'Successfully Added')

        
        
        data.netamount = request.POST.get('netamount')
        data.grossamount = request.POST.get('grossamount')
        data.markup = request.POST.get('markup')
        data.remarks = request.POST.get('remarks')
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

        data.agent_id = request.POST.get('agent')
        data.transactiontype = request.POST.get('transactiontype')
        data.transactiondate = request.POST.get('transactiondate')
        data.amount = request.POST.get('amount')
        data.referencenumber = request.POST.get('referencenumber')
        data.bankdetails = request.POST.get('bankdetails')
        data.save()
        
        
        return redirect('superadmin:stafflist')

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
            context['pre_data'] = Previllages.objects.filter(user=id).values('option')
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
        
        prev= request.POST.getlist('options')
        acc = request.POST.get('previllage')
        Previllages.objects.filter(user=data.id).delete()
       
        for i in prev:
            sub = Previllages()
            sub.user = data
            sub.option = i
            sub.acsess = acc
            sub.save()
        
        
        
        return redirect('superadmin:subadminslist')

    # Agents module end
