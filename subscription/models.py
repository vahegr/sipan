from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Section(models.Model):
    name = models.CharField(max_length=32, unique=True)
    def __str__(self):
        return f"<Section #{self.id} {self.name}>"


class SectionYear(models.Model):
    section = models.ForeignKey(Section, related_name='section_years', on_delete=models.CASCADE)
    year = models.IntegerField(null=False, validators=[MinValueValidator(1999), MaxValueValidator(2050)])
    price = models.DecimalField(null=False, decimal_places=0, max_digits=12)

    class Meta:
        unique_together = ('section', 'year')

    def __str__(self):
        return f"<SectionYear #{self.id} {self.section.name} -  {self.price} - {self.year}>"

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='user_subs', on_delete=models.CASCADE)
    year = models.ForeignKey(SectionYear, related_name='sub_year', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('year', 'user')

    def __str__(self):
        return f"<Subscription #{self.id} {self.user.full_name} - {self.year.section.name} - {self.year.year}>"