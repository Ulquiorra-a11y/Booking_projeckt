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
        fields = ('id','user','booking','booking_info','booking_info','grade')
        read_only_fields = ('id',)

    def validate_booking(self, booking):
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

