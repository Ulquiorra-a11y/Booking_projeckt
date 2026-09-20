from rest_framework import serializers

from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.users.serializers import CustomerNameSerializer
from apps.bookings.serializers import BookingShortSerializer
from core.models import BookingStatus


class ReviewSerializer(serializers.ModelSerializer):
    user = CustomerNameSerializer(source='booking.guest', read_only=True)
    booking_info = BookingShortSerializer(read_only=True, source='booking')

    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(),write_only=True)
    class Meta:
        model = Review
        fields = ('id','user','booking','description','booking_info','booking_info','grade')
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['booking'].queryset = Booking.objects.filter(
                guest=request.user,
                status=BookingStatus.COMPLETED,
                review__isnull=True,
            )

    def validate_booking(self, booking):
        """
        Ensure the selected booking is eligible for a review.

        Checks:
        - The booking belongs to the requesting user (as guest).
        - The booking's status is COMPLETED.
        - No review already exists for this booking (enforced by the
          OneToOneField, but checked here for a cleaner error message
          instead of an IntegrityError).
        """
        request = self.context['request']

        if booking.guest_id != request.user.id:
            raise serializers.ValidationError(
                'You can only leave a review for your own booking..'
            )

        if booking.status != BookingStatus.COMPLETED:
            raise serializers.ValidationError(
                'Review can only leave a review after your booking ended'
            )

        if hasattr(booking, 'review'):
            raise serializers.ValidationError(
                'Review for this booking is already completed.You can leave only one review'
            )

        return booking

