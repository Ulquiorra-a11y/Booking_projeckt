from datetime import timezone

from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from apps.listings.managers import ActiveListingManager
from core.models import UniqueID, TimeStampedModel, BookingStatus
from django.utils.translation import gettext_lazy as _


class Listing(UniqueID,TimeStampedModel):
    title = models.CharField(max_length=100, verbose_name=_("Title"), validators=[MinLengthValidator(10)])
    description = models.TextField(max_length=999, verbose_name=_("Description"), validators=[MinLengthValidator(10)])
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    house_number = models.CharField(max_length=15, verbose_name=_("House Number"))
    available = models.BooleanField(default=True, verbose_name=_("Available"))
    rooms = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)], verbose_name=_("Rooms"))
    max_guests = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)], verbose_name=_("Max Guests"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='listings',
                              verbose_name=_('Owner'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price per night"), validators=[MinValueValidator(('0.00'))])

    objects = ActiveListingManager()
    all_objects = models.Manager()


    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def __str__(self):
        return f"Listing's Title: {self.title}"

    class Meta:
        db_table = 'listings'
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        ordering = ['-created_at']

    def is_available_for(self, check_in, check_out):
        overlapping = self.bookings.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        return not overlapping.exists()


