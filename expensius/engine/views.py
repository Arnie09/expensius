from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
from login.models import Account


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

        user = request.user
        direction = request.POST.get('payload[direction]')
        amount = request.POST.get('payload[amount]')

        mapper = {'false':-1,'true':1}
        account_obj = Account.objects.get(username = user)
        account_obj.available_bal += mapper[direction]*float(amount)
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

        return redirect('/')
