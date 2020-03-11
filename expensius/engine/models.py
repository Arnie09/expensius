from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

# Create your models here.
class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(User,on_delete=models.CASCADE)
    other = models.CharField(max_length = 100, blank = True)
    direction = models.BooleanField() #True = debit False = credit
    date = models.DateTimeField()
    amount = models.FloatField()
    amount_accnt = models.FloatField()
