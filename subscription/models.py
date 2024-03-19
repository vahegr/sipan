from django.db import models
from account.models import User


class SubSection(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ForeignKey(SubSection, on_delete=models.CASCADE)
    year = models.DateField()
