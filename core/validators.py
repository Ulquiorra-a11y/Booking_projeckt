from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


phone_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{7,14}$',
    message=_("Enter a valid phone number.")
)