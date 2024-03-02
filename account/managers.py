from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, full_name, phone, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not phone:
            raise ValueError('لطفا ایمیل خود را وارد کنید!')
        if not full_name:
            raise ValueError('لطفا نام کاربری خود را انتخاب کنید')

        user = self.model(
            email=self.normalize_email(phone),
            full_name=full_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            phone=phone,
            password=password,
            full_name=full_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
