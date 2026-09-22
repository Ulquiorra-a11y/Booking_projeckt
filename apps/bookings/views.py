from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer
from apps.bookings.services import create_booking
from core.permissions import IsGuestOrReadOnly


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsGuestOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    def get_queryset(self):
        """
        Return bookings visible to the current user.

        By default, returns bookings where the user is either the guest
        who made the booking or the owner of the booked listing (combined).
        An optional `?role=` query param narrows this down:
            - `?role=guest`: only bookings the user made as a guest.
            - `?role=owner`: only bookings on listings the user owns.
        Any other or missing value falls back to the combined view.
        """
        user = self.request.user
        role = self.request.query_params.get('role')

        if role == 'guest':
            queryset = Booking.objects.filter(guest=user)
        elif role == 'owner':
            queryset = Booking.objects.filter(listing__owner=user)
        else:
            queryset = Booking.objects.filter(Q(guest=user) | Q(listing__owner=user))

        return queryset.select_related('listing', 'guest')


    def perform_create(self, serializer):
        """
        Create a booking via the `create_booking` service instead of the
        default `serializer.save()`.

        This ensures the booking goes through the full business logic in
        `create_booking` — self-booking and active-listing checks, overlap
        detection with row-level locking (`select_for_update`), and the
        confirmation email — rather than a plain model `.save()` call.

        Any `django.core.exceptions.ValidationError` raised by the service is
        converted to `rest_framework.exceptions.ValidationError` so DRF returns
        a proper 400 response instead of surfacing it as an unhandled error.
        """
        listing = serializer.validated_data['listing']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        guests_count = serializer.validated_data.get('guests_count', 1)

        try:
            booking = create_booking(
                guest=self.request.user,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                guests_count=guests_count,
            )
        except DjangoValidationError as e:
            raise DRFValidationError(e if hasattr(e, 'messages') else str(e))

        serializer.instance = booking

