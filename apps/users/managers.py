from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomerManager(BaseUserManager):
    """
    Custom manager for the Customer model, which uses email instead of
    username as the login identifier (USERNAME_FIELD = 'email').

    Required because the default Django UserManager assumes a `username`
    field; this manager normalizes the email and ensures passwords are
    always hashed via `set_password()` rather than stored in plain text.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Internal helper that builds and saves a Customer with a hashed password.

        Not intended to be called directly — use `create_user()` or
        `create_superuser()` instead.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular (non-staff, non-superuser) Customer."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self._create_user(email, password, **extra_fields)