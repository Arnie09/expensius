from django.contrib import admin
from login.models import Account
from engine.models import Transaction

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)