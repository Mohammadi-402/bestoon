from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Expense(models.Model):
    text = models.CharField(max_length = 255)
    date = models.DateTimeField(default=timezone.now)
    amount = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Income(models.Model):
    text = models.CharField(max_length = 255)
    date = models.DateTimeField(default=timezone.now)
    amount = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
