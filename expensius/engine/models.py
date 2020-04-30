from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

from login.models import Account

# Create your models here.
class Transaction(models.Model):
    transactionID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    other = models.CharField(max_length = 100, blank = True)
    direction = models.BooleanField() #True = debit False = credit
    date = models.DateTimeField()
    amount = models.FloatField()
    amount_accnt = models.FloatField()


