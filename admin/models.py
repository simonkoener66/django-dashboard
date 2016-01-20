from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.db.models.signals import pre_save

class AuthUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name='', last_name='', type='regular', id=None):
        if not email:
            raise ValueError('Users mus have an email address')

        user = self.model(email=self.normalize_email(email))
        user.is_active = True
        user.first_name = first_name
        user.last_name = last_name
        user.type = type
        user.set_password(password)
        if id:
            user.id = id
        user.save(using=self._db)

        return user


class AuthUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, blank=False, unique=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, null=False)
    type = models.CharField(max_length=20, blank=False, default='regular')
    objects = AuthUserManager()
    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return '.'.join([self.first_name[0].upper(), self.last_name[0].upper()])

    class Meta:
        db_table = 'sales_authuser'


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('AuthUser', db_constraint=False)
    type = models.CharField(max_length=20, default='')
    name = models.CharField(max_length=512, default='')
    internal_id = models.IntegerField(default=None)
    json = models.TextField(default='')
    date_created = models.DateField(auto_now_add=True, null=True)
    date_updated = models.DateField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        unique_together = ('internal_id', 'type')


class RecoverToken(models.Model):
    token = models.CharField(max_length=64, blank=False)
    date_created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('AuthUser', db_constraint=False)