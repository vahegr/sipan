from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, national_code, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not national_code:
            raise ValueError(_("National code must be set"))
        if not national_code:
            raise ValueError(_("Password code must be set"))
        user = self.model(national_code=national_code, **extra_fields)
        
        user.set_password(password)

        user = self.model(
            national_code=national_code,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, national_code, password, **extra_fields):
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
        
        return self.create_user(national_code, password, **extra_fields)
    