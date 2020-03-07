from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

from .forms import UserLoginForm, UserRegisterForm

# Create your views here.
@login_required
def home(request):
    return render(request, 'expensius/home.html')

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
        if next:
            return redirect(next)
        return redirect('/')
    
    context = {
        'forms':form
    }
    return render(request, 'expensius/register.html',context)

def logout_view(request):
    logout(request)
    return redirect('/')