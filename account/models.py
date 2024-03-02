from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    first_name = models.CharField(
        max_length=32,
    )
    last_name = models.CharField(
        max_length=64,
    )
    national_code = models.CharField(
        max_length=10,
        unique=True
    )
    phone = models.CharField(
        max_length=20,
    )
    manager = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_superuser = models.BooleanField(
        default=False,
    )
    

    objects = UserManager()

    USERNAME_FIELD = 'national_code'
    REQUIRED_FIELDS = ['first_name', 'last_name' ]


    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True
    
    @property
    def full_name(self):
        return self.first_name + " " + self.last_name
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
    
    def __str__(self):
        return self.national_code


