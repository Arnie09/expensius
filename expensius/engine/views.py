from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Transaction
from login.models import Account, Profile
from login.views import account_info, login_view
from django.http import JsonResponse
from datetime import date
from dateutil.parser import parse
import json, requests
from login.forms import AccountForm


# Create your views here.
response = {}
paginator = None

@login_required
def home(request, account = None):

    user = request.user
    profile_obj = None
    try:
        profile_obj = Profile.objects.get(user = user)
    except:
        return redirect(login_view)
    account_default = None
    account_objs = Account.objects.filter(username = profile_obj)
    if account == None:
        if len(account_objs) == 0:
            return redirect(account_info)
        account_default = account_objs[0]
    else:
        account_default = Account.objects.get(account_name = account)
    transaction_objects = Transaction.objects.filter(account = account_default).order_by('date')
    page = request.GET.get('page', 1)
    global paginator
    paginator = Paginator(transaction_objects, 10)
    number_pages = paginator.num_pages
    transactions = paginator.page(1)
    account_names = [accnt_obj.account_name for accnt_obj in account_objs]
    
    payload = {}

    payload['account_names'] = account_names
    payload['number_of_trans'] = number_pages
    payload['account_bal'] = account_default.available_bal
    payload['account_name'] = account_default.account_name
    payload['account_last_tran'] = account_default.last_trans
    payload['number_accounts'] = profile_obj.noAccount
    payload['isPaid'] = profile_obj.isPaid
    payload['number_of_transactions'] = account_default.no_transac

    return render(request, 'expensius/home.html',payload)

@login_required
def get_transaction(request):
    if request.method == "POST":
        page_no = request.POST.get('payload')
        global paginator
        transactions = None
        try:
            transactions = paginator.page(page_no)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)

        return render(request, 'expensius/get_transactions.html', {'transactions':transactions})


@login_required
def add_transacton(request, transaction_obj = None):
    print(transaction_obj)
    # ajax function 
    if request.method =="POST" or transaction_obj is not None:
        
        Message = ""
        user = request.user
        mapper = {'false':-1,'true':1}
        mapper2 = {False:-1,True:1}
        other = None
        direction = None
        account_obj = None

        if transaction_obj is None:
            direction = request.POST.get('payload[direction]')
            amount = request.POST.get('payload[amount]')
            given_date = parse(request.POST.get('payload[date]')).date()
            other = request.POST.get('payload[other]')
            change = mapper[direction]*float(amount)
            account_obj = Account.objects.get(account_name = request.POST.get('payload[account]'))
        else:
            direction = transaction_obj.direction
            print("Here",direction)
            amount = transaction_obj.amount
            given_date = transaction_obj.date.date()
            other = transaction_obj.other
            change = mapper2[direction]*float(amount)
            account_obj = transaction_obj.account

        current_date = date.today()

        profile = Profile.objects.get(user = user)
        # account_obj = Account.objects.get(username = profile)

        last_balance = None
        flag = 0

        '''
        There is always going to be a transaction in an account.
        So the scenarios are:
            - Invalid transaction by user 
                - invalid date(future)
            - Makes a transaction which is before the first transaction
        '''
        print("Here3",direction)
        if given_date > current_date:

            flag = 1
            Message = 2

        else: 

            prev_trans = Transaction.objects.filter(
                    date__lte = given_date,
                    account = account_obj
                ).order_by('-date')

            if len(prev_trans) == 0:
                last_balance = 0
            else:
                last_balance = prev_trans[:1][0].amount_accnt

            if last_balance+change<0:
                flag = 1
                Message = 3
            
            future_trans = Transaction.objects.filter(
                    date__gte = given_date,
                    account = account_obj
                ).order_by('date')

            for transaction in future_trans:
                amt = transaction.amount_accnt
                new_amt = amt+change
                if new_amt<0:
                    flag = 1
                    Message = 3
                    break

        if flag == 0:

            direction = True if direction == "true" or direction == True else False

            Message = 4
            print("Here2",direction)
            Transaction.objects.create(
                account = account_obj,
                other = other,
                direction = direction,
                amount = amount,
                date = given_date,
                amount_accnt = last_balance+change
            )
            
            account_obj.last_trans = given_date if account_obj.has_trans == False else account_obj.last_trans
            account_obj.last_trans = max(given_date, account_obj.last_trans)
            account_obj.no_transac+=1

            LAST = None
            for transaction in future_trans:
                transaction.amount_accnt += change
                LAST = transaction.amount_accnt
                transaction.save()
            account_obj.available_bal = LAST
   
            account_obj.available_bal = last_balance+change if LAST is None else account_obj.available_bal
            account_obj.has_trans = True 
            
            account_obj.save()
            
        response = {
            'mssg':Message
        }
        return JsonResponse(response)

    return redirect('/')

@login_required
def delete_transaction(request):

    if request.method=="POST":
        Message = ""
        user = request.user
        id_tran = request.POST.get('payload[id]') 
        trans_obj = Transaction.objects.filter(transactionID = id_tran)[0]
        direction = trans_obj.direction
        amount = trans_obj.amount
        given_date = trans_obj.date.date()
        current_date = date.today()
        mapper = {False:-1,True:1}
        change = mapper[direction]*float(amount)
        profile_obj = Profile.objects.get(user = user)
        account_obj = trans_obj.account
        last_balance = None
        flag = 0
        update_future = False
        transaction_set = None
        # This is for the situation when the user selects the last transaction of the user 
        if account_obj.last_trans == given_date:
            # Here two cases arise 
                # when the last transaction is also the first transaction 
                # and when the last transaction is not the first transaction

            previous_tran_obj = Transaction.objects.filter(
                    date__lte = given_date,
                    account = account_obj
                ).order_by('-date')[:2]

            if len(previous_tran_obj)>1:
                account_obj.available_bal = previous_tran_obj[1].amount_accnt
                account_obj.last_trans = previous_tran_obj[1].date
                account_obj.save()
                Message = 4
                Transaction.objects.filter(transactionID = id_tran).delete()

            elif len(previous_tran_obj) == 1:
                account_obj.available_bal -= change
                account_obj.last_trans = None
                account_obj.has_trans = False
                account_obj.save()
                Message = 4
                Transaction.objects.filter(transactionID = id_tran).delete()


        # This is for when the user will select a transaction of the user which any but the last transaction 
        else:
            future_tran_obj = Transaction.objects.filter(date__gte = given_date, account = account_obj)
            
            # we check if its possible to carry out the deletion
            for transaction in future_tran_obj:
                amt = transaction.amount_accnt
                new_amt = amt-change
                if new_amt<0:
                    flag = 1
                    Message = 3
                    break

            if flag == 0:       
                LAST = None
                for transaction in future_tran_obj:
                    transaction.amount_accnt -= change
                    LAST = transaction.amount_accnt
                    transaction.save()
                account_obj.available_bal = LAST
                account_obj.save()
                Transaction.objects.filter(transactionID = id_tran).delete()
                Message = 4

        if Message == 4:
            account_obj.no_transac -= 1 
            account_obj.save()

        response = {
            'mssg':Message
        }
        return JsonResponse(response)

    return redirect('/')

@login_required
def edit_transaction(request):

    if request.method == "POST":
        old_tran = Transaction.objects.get(transactionID = request.POST.get('payload[id]'))
        delete_transaction(request)
        message = json.loads(add_transacton(request).content)["mssg"]
        
        response = {
            'mssg':message
        }

        if message != 4:
            add_transacton(request,old_tran)
            
        return JsonResponse(response)
        
    return redirect('/')

@login_required
def delete_all_transaction(request):
    
    if request.method == "POST":
        Message = None
        password = request.POST.get('payload[password]')
        account = request.POST.get('payload[account]')
        user = request.user
        profile_obj = Profile.objects.get(user = user)
        if user.check_password(password):
            account_obj = Account.objects.get(account_name = account)
            transactions = Transaction.objects.filter(account = account_obj)
            for transaction in transactions:
                transaction.delete()
            account_obj.delete()
            profile_obj.noAccount-=1
            profile_obj.save()
            Message = 2
        else:
            Message = 1
        
        response = {
            'mssg':Message
        }

        return JsonResponse(response)

    return redirect('/')

@login_required
def search_transaction(request):

    if request.method == "POST":

        user = request.user
        profile_obj = Profile.objects.get(user = user)
        account = request.POST.get('account')
        accnt_obj = Account.objects.get(account_name = account, username = profile_obj)
        transaction_obj = Transaction.objects.filter(account = accnt_obj)

        try:
            amt_ub = request.POST.get('smaller_than')
            transaction_obj = transaction_obj.filter(amount__lte = amt_ub )
        except:
            pass

        try:
            amt_lb = request.POST.get('greater_than')
            transaction_obj = transaction_obj.filter(amount__gte = amt_lb)
        except:
            pass
        
        try:
            other = request.POST.get('search_other')
            if other != "":
                transaction_obj = transaction_obj.filter(other = other)
        except:
            pass

        try:
            direction = request.POST.get("direction")
            if direction == "Credit" or direction == "Debit":
                direc = False if direction == "Debit" else True
                transaction_obj = transaction_obj.filter(direction = direc)
        except:
            pass
        
        show = True if len(transaction_obj)>0 else False
        
        response = {
            'account' : accnt_obj.account_name,
            'transactions' : transaction_obj,
            'show':show
        }
        
        return render(request, 'expensius/search.html', response)

    return redirect('/')