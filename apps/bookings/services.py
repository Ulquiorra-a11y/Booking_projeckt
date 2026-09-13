from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking, BookingStatus


def create_booking(*, guest, listing, check_in, check_out, guests_count):
    if listing.owner_id == guest.id:
        raise ValidationError(_('You cannot book your own listing.'))
    if not listing.is_active:
        raise ValidationError(_('This listing is not available for booking.'))

    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValidationError(_('Check-out date must be after check-in date.'))
    total_price = nights * listing.price

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
            total_price=total_price,
            guests_count=guests_count

        )
        booking.save()

        return booking