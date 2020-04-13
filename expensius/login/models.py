from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    username = models.OneToOneField(User,on_delete=models.CASCADE)
    account_name = models.TextField()
    available_bal = models.FloatField(default=0)
    has_trans = models.BooleanField(null = True)
    last_trans = models.DateField(null = True)
    num_bal = models.IntegerField(default=0)