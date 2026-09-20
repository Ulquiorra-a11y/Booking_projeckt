from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q,F
from core.validators import validate_not_in_past, validate_date


from core.models import UniqueID, TimeStampedModel, Guests, BookingStatus
from django.utils.translation import gettext_lazy as _


class Booking(UniqueID,TimeStampedModel):
    """
        Represents a guest's reservation for a specific listing.

        A booking always belongs to exactly one listing and one guest. Model-level
        validation (see `clean()`) enforces that the listing is active, the
        check-out date is after check-in, and the requested date range does not
        overlap with any other PENDING or CONFIRMED booking on the same listing.
        `total_price` is set once at creation time and is not recalculated
        automatically if the listing's price changes afterward.
    """
    guest = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='bookings',
                              verbose_name=_('Guest'))
    listing = models.ForeignKey('listings.Listing',on_delete=models.PROTECT,related_name='bookings',
                                verbose_name=_('Listing'))
    check_in = models.DateField(verbose_name=_('Check In'),validators=[validate_not_in_past])
    check_out = models.DateField(verbose_name=_('Check Out'))
    guests_count = models.PositiveIntegerField(choices=Guests,default=Guests.ONE,verbose_name=_('Guests Count'))
    status = models.CharField(choices=BookingStatus,default=BookingStatus.PENDING,max_length=10,verbose_name=_('Status'))
    total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name=_('Total Price'))

    def clean(self):
        """
        Validate the booking before it is saved.
        """
        super().clean()

        if self.listing and not self.listing.is_active:
            raise ValidationError(_('This listing is not available for booking.'))

        if self.check_in and self.check_out:
            validate_date(self.check_in, self.check_out)

        overlapping = Booking.objects.filter(listing=self.listing,status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=self.check_out,check_out__gt=self.check_in,).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(_('These dates are already booked for this listing.'))

    def save(self, *args, **kwargs):
        """
        Save the booking after running full model validation.
        """
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Booking: {self.listing.title} ({self.check_in} → {self.check_out})"

    class Meta:
        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ('-check_in',)
        constraints = [models.CheckConstraint(condition=Q(check_out__gt=F('check_in')),name="check_out_after_checkin"),]
        indexes = [
            models.Index(fields=['listing', 'check_in', 'check_out'], name='booking_listing_dates_idx'),
            models.Index(fields=['status'], name='booking_status_idx'),
            models.Index(fields=['-check_in'], name='booking_check_in_idx'),
        ]


