from django.db.models import Q
from django.shortcuts import render
from rest_framework.exceptions import ValidationError as DRFValidationError
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

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_create(self, serializer):
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

