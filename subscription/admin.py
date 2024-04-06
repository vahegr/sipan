from django.contrib import admin

from .models import Section, SectionYear, Subscription
# Register your models here.
admin.site.register(Subscription)
admin.site.register(SectionYear)
admin.site.register(Section)
