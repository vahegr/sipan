from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser


class UserField(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Year(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class User(AbstractBaseUser):
    years = models.ManyToManyField(Year)
    field = models.ManyToManyField(UserField)
    phone = models.CharField(
        max_length=20,
        unique=True,
    )
    full_name = models.CharField(
        max_length=100,
    )
    manager = models.BooleanField(
        default=False,
    )
    employee = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name', ]

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        " Is the user a member of staff? "
        # Simplest possible answer: All admins are staff
        return self.is_admin


