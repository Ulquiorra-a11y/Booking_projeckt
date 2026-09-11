from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


MAX_AGE_YEARS = 120
MAX_BOOKING_ADVANCE_DAYS = 365

phone_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{7,14}$',
    message=_("Enter a valid phone number.")
)


def validate_not_in_past(value):
    if value < timezone.now().date():
        raise ValidationError(_('Date cannot be in the past.'))


def validate_date(start_date, end_date):
    if end_date <= start_date:
        raise ValidationError(_('End date must be after start date.'))



def validate_birth_date(value):
    today = timezone.now().date()

    if value > today:
        raise ValidationError(_('Birth date cannot be in the future.'))

    min_allowed_date = today - timedelta(days=MAX_AGE_YEARS * 365)
    if value < min_allowed_date:
        raise ValidationError(_('Age cannot exceed %(max_age)s years.'), params={'max_age': MAX_AGE_YEARS})


def validate_not_too_far_in_future(value):
    max_allowed_date = timezone.now().date() + timedelta(days=MAX_BOOKING_ADVANCE_DAYS)
    if value > max_allowed_date:
        raise ValidationError(
            _('Booking cannot be made more than %(days)s days in advance.'),
            params={'days': MAX_BOOKING_ADVANCE_DAYS})