from django.db import models
from django.db.models import Q

from core.models import UniqueID, TimeStampedModel, Grades
from django.utils.translation import gettext_lazy as _


class Review(TimeStampedModel, UniqueID):
    """
    Represents a guest's review of a completed booking.

    Tied one-to-one to a Booking rather than directly to a user/listing pair,
    so a review can only exist for a booking that actually happened, and a
    booking can have at most one review. `user` and `listing` are exposed as
    read-only convenience properties derived from the related booking,
    avoiding duplicated foreign keys that could drift out of sync.
    """
    booking = models.OneToOneField('bookings.Booking',on_delete=models.CASCADE,related_name='review',
                                   verbose_name=_('Booking'))
    description = models.TextField(verbose_name=_('Description'),max_length=255)
    grade = models.PositiveIntegerField(choices=Grades,verbose_name=_('Grade'))

    @property
    def user(self):
        """
        Return the guest who made the reviewed booking
        """
        return self.booking.guest

    @property
    def listing(self):
        """
        Return the listing that was reviewed
        """
        return self.booking.listing

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'reviews'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=Q(grade__gte=1) & Q(grade__lte=5), name='grade_between_1_and_5')]
        indexes = [
            models.Index(fields=['-created_at'], name='review_created_at_idx'),
            models.Index(fields=['grade'], name='review_grade_idx'),
        ]

