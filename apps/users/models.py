from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.users.managers import CustomerManager
from core.models import UniqueID, TimeStampedModel
from django.utils.translation import gettext_lazy as _

from core.validators import phone_validator


class Customer(UniqueID,TimeStampedModel,AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50,verbose_name=_('First Name'))
    last_name = models.CharField(max_length=50,verbose_name=_('Last Name'))
    email = models.EmailField(unique=True , max_length=250, verbose_name=_("Email"))
    birth_date = models.DateField(verbose_name=_('Birth Date'),blank=True, null=True)
    phone_number = models.CharField(max_length=20,validators=[phone_validator],verbose_name=_('Phone Number'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Staff status'))

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"

    class Meta:
        db_table = 'customers'
        ordering = ('-created_at',)
        get_latest_by = 'created_at'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

