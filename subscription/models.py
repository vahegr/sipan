import re
from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


def validate_hex_color(value):
    regex = r'^#[0-9a-fA-F]{6}$'
    if not re.match(regex, value):
        raise ValidationError('Invalid hex color format')


class Section(models.Model):
    name = models.CharField(max_length=32, unique=True)
    color = models.CharField(max_length=7, validators=[validate_hex_color], default="#000000")

    def __str__(self):
        return f"<Section #{self.id} {self.name} {self.color}>"


class SectionYear(models.Model):
    section = models.ForeignKey('subscription.Section', related_name='section_years', on_delete=models.CASCADE)
    year = models.IntegerField(null=False, validators=[MinValueValidator(1999), MaxValueValidator(2050)])
    price = models.DecimalField(null=False, decimal_places=0, max_digits=12)

    class Meta:
        unique_together = ('section', 'year')

    def __str__(self):
        return f"<SectionYear #{self.id} {self.section.name} -  {self.price} - {self.year}>"


class Subscription(models.Model):
    user = models.ForeignKey('account.User', related_name='user_subs', on_delete=models.CASCADE)
    section_year = models.ForeignKey('subscription.SectionYear', related_name='sub_year', on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1000)])
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('section_year', 'user')

    def __str__(self):
        return f"<Subscription #{self.id} {self.user.full_name} - {self.section_year.section.name} - {self.section_year.year}>"


class History(models.Model):
    user = models.ForeignKey('account.User', related_name='user_sectionhistory', on_delete=models.CASCADE)
    section = models.ForeignKey('subscription.Section', related_name='section_history', on_delete=models.CASCADE)
    date_changed = models.DateField()
