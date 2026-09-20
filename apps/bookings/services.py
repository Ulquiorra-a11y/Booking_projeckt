from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking, BookingStatus


def send_booking_confirmation_email(booking):
    """
    Send a booking confirmation email to the guest.
    """
    subject = 'Booking confirmation'
    message = (
        f'Hello, {booking.guest.first_name}!\n\n'
        f'Your booking is confirmed.\n'
        f'House: {booking.listing.title}\n'
        f'Dates: {booking.check_in} — {booking.check_out}\n'
        f'Price: {booking.total_price}\n'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.guest.email],
        fail_silently=False,
    )


def create_booking(*, guest, listing, check_in, check_out, guests_count):
    """
    Create a new booking for a listing, with validation and conflict protection.
    :param guest: The user making the booking.
    :param listing: The listing being booked.
    :param check_in: The check-in date.
    :param check_out: The check-out date.
    :param guests_count: Number of guests for this booking.
    :return: Booking: The newly created and saved booking instance.
    """
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
        send_booking_confirmation_email(booking)
        return booking