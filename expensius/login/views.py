from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
from .models import Account, Profile
from engine.models import Transaction
from datetime import date

from .forms import UserLoginForm, UserRegisterForm, AccountForm

# Create your views here.
def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username = username, password = password)
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        if next:
            return redirect(next)
        return redirect('/')
    
    context = {
        'forms':form
    }
    return render(request, 'expensius/login.html',context)

def register_view(request):
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        password = form.cleaned_data.get('password')
        user = form.save(commit = False)
        user.set_password(password)
        user.save()
        new_user = authenticate(username = user.username, password = password)
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        Profile.objects.create(
            user = user,
        )
        if next:
            return redirect(next)
        return redirect('account/')
    
    context = {
        'forms':form
    }
    return render(request, 'expensius/register.html',context)

@login_required
def account_info(request):
    form = AccountForm(request.POST or None)
    if form.is_valid():
        user = request.user
        profile = Profile.objects.filter(user = user)[0]
        accnt_name = form.cleaned_data.get('accountname')
        initial_bal = form.cleaned_data.get('current_bal')
        has_transaction = True
        last_trans_date = date.today()

        account  = Account(
            username=profile,
            account_name=accnt_name,
            available_bal=initial_bal,
            has_trans = has_transaction,
            last_trans = last_trans_date,
            no_transac = 1
            )

        account.save()

        Transaction.objects.create(
            account = account,
            other = user.username,
            direction = True,    
            date = last_trans_date,
            amount = initial_bal,
            amount_accnt = initial_bal
        )

        profile.noAccount+=1
        profile.save()

        return redirect('about')

    context = {
        'forms':form
    }
    return render(request, 'expensius/fillaccnt.html',context)

# function that renders logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

# function that renders the about page
def about(request):
    return render(request, 'expensius/about.html')