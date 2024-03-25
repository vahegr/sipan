from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Section(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='users', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='section', on_delete=models.CASCADE)
    year = models.IntegerField(null=False, validators=[MinValueValidator(1999), MaxValueValidator(2050)])
