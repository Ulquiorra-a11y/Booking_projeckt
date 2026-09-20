from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.utils import timezone

from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator, FileExtensionValidator
from django.db import models

from apps.listings.managers import ActiveListingManager
from core.models import UniqueID, TimeStampedModel, BookingStatus
from django.utils.translation import gettext_lazy as _


MAX_PHOTOS = 6


class Listing(UniqueID,TimeStampedModel):
    """
    Represents a property listed for booking by its owner.

    Availability is tracked in two independent ways: `is_active` reflects
    whether the owner has published the listing at all, while date-specific
    availability (whether it's free for a given check-in/check-out range) is
    computed on demand via `is_available_for()` or `ActiveListingManager`,
    not stored as a field. Deletion is soft (see `delete()`); `objects` only
    returns non-deleted listings, while `all_objects` includes everything.
    """
    title = models.CharField(max_length=100, verbose_name=_("Title"), validators=[MinLengthValidator(10)])
    description = models.TextField(max_length=999, verbose_name=_("Description"), validators=[MinLengthValidator(10)])
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    house_number = models.CharField(max_length=15, verbose_name=_("House Number"))
    is_active = models.BooleanField(default=True, verbose_name=_("Available"))
    rooms = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)], verbose_name=_("Rooms"))
    max_guests = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)], verbose_name=_("Max Guests"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='listings',
                              verbose_name=_('Owner'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price per night"),
                                validators=[MinValueValidator(Decimal('0.01'))])

    objects = ActiveListingManager()
    all_objects = models.Manager()

    @property
    def main_photo(self):
        """
        Return the listing's main photo, or None if none is marked as main.
        """
        return self.photos.filter(is_main=True).first()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def average_rating(self):
        """
        Return the average review grade across all bookings, or None if there are no reviews.
        """
        return self.bookings.filter(review__isnull=False).aggregate(avg=Avg('review__grade'))['avg']

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
        indexes = [
            models.Index(fields=['city', 'country'], name='listing_city_country_idx'),
            models.Index(fields=['is_active'], name='listing_is_active_idx'),
            models.Index(fields=['deleted_at'], name='listing_deleted_at_idx'),
            models.Index(fields=['price'], name='listing_price_idx'),
            models.Index(fields=['-created_at'], name='listing_created_at_idx'),
        ]

    def is_available_for(self, check_in, check_out):
        """
        Check whether this listing has no PENDING or CONFIRMED booking
        overlapping the given date range.
        :param check_in: Requested check-in date.
        :param check_out: Requested check-out date.
        :return: bool: True if the listing is free for the given dates.
        """
        overlapping = self.bookings.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        return not overlapping.exists()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Photos(TimeStampedModel,UniqueID):
    """
    Represents a single photo attached to a listing.

    A listing may have at most `MAX_PHOTOS` photos (enforced in `clean()`
    on creation only). At most one photo per listing can be marked as
    `is_main`; setting a new one automatically unmarks the previous one
    (see `save()`).
    """
    image = models.ImageField(upload_to='photos/%Y/%m', verbose_name=_("Photo"),
                              validators=[FileExtensionValidator(['jpg', 'png','jpeg'])])
    listing = models.ForeignKey('Listing',on_delete=models.CASCADE,verbose_name=_("Listing"),related_name='photos')
    is_main = models.BooleanField(default=False, verbose_name=_("Main"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    def __str__(self):
        return f"Photo for {self.listing.title}"

    class Meta:
        db_table = 'photos'
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
        ordering = ['order','created_at']
        indexes = [
            models.Index(fields=['listing', 'order'], name='photo_listing_order_idx'),
            models.Index(fields=['listing', 'is_main'], name='photo_listing_is_main_idx'),
        ]

    def clean(self):
        """
        Enforce the per-listing photo limit on creation.

        Only checked for new photos (not on updates to an existing photo),
        since the count should not block edits to already-saved records.
        """
        super().clean()

        is_new = not Photos.objects.filter(pk=self.pk).exists()
        if is_new and self.listing_id:
            current_count = Photos.objects.filter(listing_id=self.listing_id).count()
            if current_count >= MAX_PHOTOS:
                raise ValidationError(_('A listing cannot have more than %(max)s photos.'),params={'max': MAX_PHOTOS})

    def save(self, *args, **kwargs):
        """
        Save the photo after full validation.

        If this photo is marked as `is_main`, any other main photo on the
        same listing is automatically unmarked first, so a listing never
        ends up with more than one main photo.
        """
        self.full_clean()

        if self.is_main:
            Photos.objects.filter(listing_id=self.listing_id, is_main=True).exclude(pk=self.pk).update(is_main=False)

        super().save(*args, **kwargs)