from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow read access to anyone; allow write access only to the object's
    owner (matched via `obj.owner_id`). Used for Listing.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id

class IsReviewCreatorOrReadOnly(BasePermission):
    """
    Allow read access to anyone; allow write access only to the guest who
    made the booking the review is attached to (via `obj.booking.guest_id`).
    Used for Review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.booking.guest_id == request.user.id

class IsGuestOrReadOnly(BasePermission):
    """
    Used for Booking. Read access is allowed to both the guest who made the
    booking and the owner of the booked listing, so a host can see who has
    booked their property. Write access is restricted to the guest only —
    the listing owner cannot modify a booking made against their listing.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.guest_id == request.user.id or obj.listing.owner_id == request.user.id
        return obj.guest_id == request.user.id