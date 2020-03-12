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
        last_balance = None
        flag = 0
        update_future = False
        transaction_set = None

        if account_obj.has_trans == False:

            # This is the case when there has beeen no previous transactions
            current_bal = account_obj.available_bal
            future_bal = current_bal+change
            if future_bal<0:
                #error, balance in account cannot be negetive
                flag = 1
                Message = 1
            elif given_date>current_date:
                flag = 1
                Message = 2
            else:
                last_balance = account_obj.available_bal
                Message = 4
                account_obj.has_trans = True
                account_obj.last_trans = given_date
                account_obj.save()

        else:

            # this is the case when there has been previous transactions

            #here comes 2 cases, 
                #case 1: when the date of the new transaction > date of last inserted transaction 
                #case 2: when the date of the new transaction is in between the last inserted transaction

            last_date = account_obj.last_trans
            if given_date>last_date:

                # We check whether the new balancce is going to be negetive or not 
                current_bal = account_obj.available_bal
                future_bal = current_bal+change
                if future_bal<0:
                    flag = 1
                    Message = 1
                elif given_date>current_date:
                    flag = 1
                    Message = 2
                else:
                    last_balance = account_obj.available_bal
                    Message = 4

            else:

                # first we check if the given date is a valid date or not
                if given_date>current_date:
                    flag  = 1
                    Message = 2
                else:
                    last_balance_obj = Transaction.objects.filter(date__lte = given_date).order_by('date')[:1]
                    print(last_balance_obj)
                    last_balance = last_balance_obj[0].amount_accnt
                    if last_balance+change<0:
                        flag = 1
                        Message = 1
                    else:
                        transaction_set = Transaction.objects.filter(date__gt = given_date,date__lte = current_date).order_by('date')
                        flag2 = 0
                        for transaction in transaction_set:
                            amt = transaction.amount_accnt
                            new_amt = amt+change
                            if new_amt<0:
                                flag2 = 1
                                break
                        if flag2 == 0:
                            update_future = True
                            Message = 4
                        else:
                            flag = 1
                            Message = 3


        if flag == 0:
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
                amount_accnt = last_balance+change
            )

            if given_date>account_obj.last_trans:
                account_obj.last_trans = given_date

            if update_future == True:
                LAST = None
                for transaction in transaction_set:
                    transaction.amount_accnt += change
                    LAST = transaction.amount_accnt
                    transaction.save()
                account_obj.available_bal = LAST
            else:
                account_obj.available_bal = last_balance+change

            account_obj.save()

        response = {
            'mssg':Message\
        }
        return JsonResponse(response)




        # last_inserted_date = Transaction.objects.latest('date')
        # print(last_inserted_date)
        # if last_inserted_date == None:
        #     print("No transactions")

        # previous_transaction = Transaction.objects.filter(date__lte = given_date).order_by('date')[:1]
        # previous_balance = 0 
        # print(previous_transaction)
        # if len(previous_transaction) == 0:
        #     previous_balance = current_bal
        # else:
        #     previous_balance = previous_transaction.amount_accnt


        # elif given_date > current_date:
        #     #error, date cannot be a future date
        #     Message = 2
        # else:
        #     transaction_set = Transaction.objects.filter(date__gt = given_date,date__lte = current_date).order_by('date')
        #     flag = 0
            
        #     for transaction in transaction_set:
        #         amt = transaction.amount_accnt
        #         new_amt = amt+change
        #         if new_amt<0:
        #             Message = 3
        #             flag = 1
        #             break

        #     if flag == 0:
    
        #         if direction == 'true':
        #             direction = True
        #         elif direction == 'false':
        #             direction = False

        #         Transaction.objects.create(
        #             account = user,
        #             other = request.POST.get('payload[other]'),
        #             direction = direction,
        #             amount = amount,
        #             date = request.POST.get('payload[date]'),
        #             amount_accnt = previous_balance+change
        #             )

        #         if len(transaction_set) == 0:
        #             account_obj.available_bal+=change
        #             account_obj.save()
        #         Message = 4
        #         LAST = None
        #         for transaction in transaction_set:
        #             transaction.amount_accnt += change
        #             LAST = transaction.amount_accnt
        #             transaction.save()
        #         account_obj.available_bal = LAST
        #         account_obj.save()
        # response = {
        #     'mssg':Message
        # }
        # return JsonResponse(response)
    return redirect('/')

@login_required
def delete_transaction(request):

    if request.method=="POST":
        Message = ""
        user = request.user
        id_tran = request.POST.get('payload[id]') 
        direction = request.POST.get('payload[direction]')
        amount = request.POST.get('payload[amount]')
        print(amount)
        given_date = parse(request.POST.get('payload[date]')).date()
        current_date = date.today()
        mapper = {'false':-1,'true':1}
        change = mapper[direction]*float(amount)

        transaction_set = Transaction.objects.filter(date__gt = given_date,date__lte = current_date).order_by('date')
        flag = 0
        for transaction in transaction_set:
            amt = transaction.amount_accnt
            new_amt = amt-change
            if new_amt<0:
                Message = 3
                flag = 1
                break

        if flag == 0:
            Transaction.objects.filter(id=id_tran).delete()
            for transaction in transaction_set:
                    transaction.amount_accnt -= change
                    transaction.save()
            Message = 4

        response = {
            'mssg':Message
        }
        return JsonResponse(response)

    return redirect('/')

@login_required
def edit_transaction(request):
    return redirect('/')