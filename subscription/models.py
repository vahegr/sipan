from datetime import datetime
import re

from django.db import models
from django.db.models import Q, OuterRef, Subquery, Exists
from account.models import User
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

    def get_members(self):
        history_subquery = History.objects.filter(Q(user_id=OuterRef('pk')) & Q(date_changed__year__lte=9999)).order_by('-date_changed')
        users_query = User.objects.annotate(section=Subquery(history_subquery.values('section')[:1])).filter(section=self.pk)
        return users_query


class SectionYear(models.Model):
    section = models.ForeignKey(Section, related_name='section_years', on_delete=models.CASCADE)
    year = models.IntegerField(null=False, validators=[MinValueValidator(1999), MaxValueValidator(2050)])
    price = models.DecimalField(null=False, decimal_places=0, max_digits=12)

    class Meta:
        unique_together = ('section', 'year')

    def __str__(self):
        return f"<SectionYear #{self.id} {self.section.name} -  {self.price} - {self.year}>"

    def get_members(self, search=None):
        history_subquery = History.objects.filter(Q(user_id=OuterRef('pk')) & Q(date_changed__year__lte=self.year)).order_by('-date_changed')
        payment_subquery = Subscription.objects.filter(Q(user_id=OuterRef('pk')) & Q(year=self.pk))
        payment_paid_subquery = payment_subquery.filter(Q(amount__gt=0))
        users_query = User.objects.annotate(section=Subquery(history_subquery.values('section')[:1]), payment=Subquery(payment_paid_subquery.values('id')[:1]), has_paid=Exists(payment_paid_subquery), amount=Subquery(payment_subquery.values('amount')[:1])).filter(section=self.section)
        return users_query


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='user_subs', on_delete=models.CASCADE)
    year = models.ForeignKey(SectionYear, related_name='sub_year', on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    date_created = models.DateField()

    class Meta:
        unique_together = ('year', 'user')

    def __str__(self):
        return f"<Subscription #{self.id} {self.user.full_name} - {self.year.section.name} - {self.year.year}>"


class History(models.Model):
    user = models.ForeignKey(User, related_name='user_sectionhistory', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='section_history', on_delete=models.CASCADE)
    date_changed = models.DateField()
