from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking, BookingStatus


def create_booking(*, guest, listing, check_in, check_out, **kwargs):
    with transaction.atomic():
        conflicting = Booking.objects.select_for_update().filter(
            listing=listing,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        list(conflicting)

        if conflicting.exists():
            raise ValidationError(_('These dates are already booked.'))

        booking = Booking(
            guest=guest,
            listing=listing,
            check_in=check_in,
            check_out=check_out,
            **kwargs
        )
        booking.save()

        return booking