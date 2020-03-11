from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
from login.models import Account
from django.http import JsonResponse
from datetime import date
from dateutil.parser import parse

# Create your views here.
@login_required
def home(request):
    user = request.user
    account_obj = Account.objects.get(username = user)
    transaction_objects = Transaction.objects.filter(account = user).order_by('date')[:50]
    
    payload = {}

    if transaction_objects == None:
        payload['transactions'] = -1
    else:
        payload['transactions_len'] = len(transaction_objects)
        payload['transactions'] = transaction_objects
        payload['transaction_id'] = []
        payload['transaction_with'] = []
        payload['transaction_amt'] = []
        payload['transaction_date'] = []
        payload['transaction_direction'] = []
        payload['transaction_history'] = []

        for transaction in transaction_objects:
            payload['transaction_id'].append(str(transaction.id))
            payload['transaction_with'].append(transaction.other)
            payload['transaction_amt'].append(transaction.amount)
            payload['transaction_date'].append(transaction.date)
            payload['transaction_direction'].append(transaction.direction)
            payload['transaction_history'].append(transaction.amount_accnt)

    payload['account_bal'] = account_obj.available_bal
    payload['account_name'] = account_obj.account_name

    return render(request, 'expensius/home.html',payload)

@login_required
def add_transacton(request):

    # ajax function 
    if request.method =="POST":

        Message = ""
        user = request.user
        direction = request.POST.get('payload[direction]')
        amount = request.POST.get('payload[amount]')
        given_date = parse(request.POST.get('payload[date]')).date()
        current_date = date.today()
        mapper = {'false':-1,'true':1}
        change = mapper[direction]*float(amount)

        account_obj = Account.objects.get(username = user)

        current_bal = account_obj.available_bal
        future_bal = current_bal+change

        if future_bal<0:
            #error, balance in account cannot be negetive
            Message = 1
        elif given_date > current_date:
            #error, date cannot be a future date
            Message = 2
        else:
            transaction_set = Transaction.objects.filter(date__gt = given_date,date__lte = current_date).order_by('date')
            flag = 0
            for transaction in transaction_set:
                amt = transaction.amount_accnt
                new_amt = amt+change
                if new_amt<0:
                    Message = 3
                    flag = 1
                    break

            if flag == 0:
    
                account_obj.available_bal += change
                if direction == 'true':
                    direction = True
                elif direction == 'false':
                    direction = False

                Transaction.objects.create(
                    account = user,
                    other = request.POST.get('payload[other]'),
                    direction = direction,
                    amount = amount,
                    date = request.POST.get('payload[date]'),
                    amount_accnt = account_obj.available_bal
                    )

                account_obj.save()
                Message = 4

                for transaction in transaction_set:
                    transaction.amount_accnt += change
                    transaction.save()

        response = {
            'mssg':Message
        }
        return JsonResponse(response)
