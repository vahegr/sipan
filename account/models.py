import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import validate_email
from django.utils.timezone import now

from .managers import UserManager


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.national_code}-{uuid.uuid4()}.{ext}"
    return os.path.join('user-images', filename)


class User(AbstractBaseUser):
    image = models.ImageField(upload_to=get_file_path, null=True)
    first_name = models.CharField(
        max_length=32,
    )
    last_name = models.CharField(
        max_length=64,
    )
    first_name_fa = models.CharField(
        max_length=32,
        blank=True,
        default=''
    )
    last_name_fa = models.CharField(
        max_length=64,
        blank=True,
        default=''
    )
    username = models.CharField(
        max_length=16,
        unique=True
    )
    national_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        default=None
    )
    phone = models.CharField(
        max_length=11,
        blank=True,
        default=''
    )
    email = models.CharField(
        max_length=64,
        blank=True,
        default='',
        validators=[validate_email]
    )
    address = models.CharField(
        max_length=256,
        blank=True,
        default=''
    )
    home = models.CharField(
        max_length=11,
        blank=True,
        default=''
    )
    manager = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=False,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_superuser = models.BooleanField(
        default=False,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_registered = models.DateField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def has_perm(self, perm, obj=None):
        return True

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name_fa(self):
        return f'{self.first_name_fa} {self.last_name_fa}'

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return f"< {self.id} {self.username} {self.national_code} >"
