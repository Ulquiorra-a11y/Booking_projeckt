from django.db import models


class ActiveListingManager(models.Manager):
    """
     Default manager for Listing that excludes soft-deleted rows.

    Used as `Listing.objects`, so any query through the default manager
    (e.g. `Listing.objects.all()`, `Listing.objects.filter(...)`)
    automatically omits listings with `deleted_at` set. Use
    `Listing.all_objects` to include soft-deleted listings as well.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)