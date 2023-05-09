from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


def logo_directory_path(instance, filename):
    return f'images/user_{instance.id}/logo/{filename}'


class UserManager(BaseUserManager):
    def create_user(self, email, fullname, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not fullname:
            raise ValueError('Users must have a full name')

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password):
        user = self.create_user(
            email=email,
            fullname=fullname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    fullname = models.CharField(verbose_name='Fullname', max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    age = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    university = models.CharField(max_length=256, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=logo_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
