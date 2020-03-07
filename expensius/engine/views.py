from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
from login.models import Account


# Create your views here.
@login_required
def home(request):
    return render(request, 'expensius/home.html')

@login_required
def add_transacton(request):

    if request.method =="POST":

        user = request.user
        direction = request.POST.get('payload[direction]')
        amount = request.POST.get('payload[amount]')
        dir_bool = None
        if direction == "on":
            dir_bool = False
        else:
            dir_bool = True

        Transaction.objects.create(
            account = user,
            other = request.POST.get('payload[other]'),
            direction = dir_bool,
            amount = amount,
            date = request.POST.get('payload[date]')
            )

        mapper = {False:1,True:-1}
        account_obj = Account.objects.get(username = user)
        print(account_obj.available_bal)
        account_obj.available_bal += mapper[dir_bool]*float(amount)
        print(account_obj.available_bal)
        account_obj.save()

        return redirect('/')
