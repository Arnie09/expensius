from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profileID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    noAccount = models.IntegerField(default=0)

    def __str__(self):
        return "%s %s" % (self.user.username, self.noAccount)

# Create your models here.
class Account(models.Model):
    accountID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.ForeignKey(Profile,on_delete=models.CASCADE)
    account_name = models.TextField()
    available_bal = models.FloatField(default=0)
    has_trans = models.BooleanField(null = True)
    last_trans = models.DateField(null = True)
    no_transac = models.IntegerField(default=0)

    def __str__(self):
        return "%s %s" % (self.account_name, self.no_transac)
