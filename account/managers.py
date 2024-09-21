from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import OuterRef, Subquery, Q, Exists, QuerySet

from subscription.models import History, SectionYear, Subscription


class UsersQuerySet(QuerySet):
    def in_section(self, section, year, payment=False):
        history_subquery = History.objects.filter(Q(user_id=OuterRef('pk')) & Q(date_changed__year__lte=year)).order_by('-date_changed')
        result = self.annotate(section=Subquery(history_subquery.values('section')[:1]))

        if payment:
            founded_year = SectionYear.objects.filter(section=section, year=year).first()
            payment_subquery = Subscription.objects.filter(Q(user_id=OuterRef('pk')) & Q(section_year=founded_year))
            payment_paid_subquery = payment_subquery.filter(Q(amount__gt=0))
            result = result.annotate(payment=Subquery(payment_paid_subquery.values('id')[:1]), has_paid=Exists(payment_paid_subquery), amount=Subquery(payment_subquery.values('amount')[:1]))

        return result.order_by('pk').filter(section=section)

    def search(self, search):
        if search:
            filters = Q()
            for search_val in search.split():
                filters = filters | Q(national_code__icontains=search_val) | Q(first_name__icontains=search_val) | Q(last_name__icontains=search_val)
            return self.filter(filters)
        else:
            return self


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UsersQuerySet(self.model, using=self._db)

    def in_section(self, *args, **kwargs):
        return self.get_queryset().in_section(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.get_queryset().search(*args, **kwargs)

    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(_("Username must be set"))
        if not username:
            raise ValueError(_("Password code must be set"))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)

        user = self.model(
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)
