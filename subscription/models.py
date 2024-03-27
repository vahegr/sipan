from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Section(models.Model):
    name = models.CharField(max_length=32, unique=True)


class SectionYear(models.Model):
    section = models.ForeignKey(Section, related_name='section_years', on_delete=models.CASCADE)
    year = models.IntegerField(null=False, validators=[MinValueValidator(1999), MaxValueValidator(2050)])
    price = models.DecimalField(null=False, decimal_places=0, max_digits=12)

    class Meta:
        unique_together = ('section', 'year')

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='user_subs', on_delete=models.CASCADE)
    year = models.ForeignKey(SectionYear, related_name='sub_year', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('year', 'user')