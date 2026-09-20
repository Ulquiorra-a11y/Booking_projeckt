from datetime import timezone

from django.core.exceptions import ValidationError as ValidationErrorCore
from rest_framework import serializers

from apps.bookings.models import Booking
from apps.listings.models import Listing
from core.validators import validate_date


class BookingSerializer(serializers.ModelSerializer):
    listing = serializers.HyperlinkedRelatedField(
        view_name='listing-detail',queryset=Listing.objects.filter(is_active=True))
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    guest_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Booking
        fields = ('id','listing','listing_title','guest_name','check_in','check_out','guests_count','status','total_price',
                  'created_at')
        read_only_fields = ('id', 'status', 'total_price', 'created_at')

    def get_guest_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}"

    def validate(self, data):
        """
        Cross-field validation: ensure check-out is after check-in.
        """
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in and check_out:
            validate_date(check_in, check_out)
        return data

class BookingShortSerializer(serializers.ModelSerializer):
    listing = serializers.HyperlinkedRelatedField(
        view_name='listing-detail', queryset=Listing.objects.filter(is_active=True))
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = ('id','listing','listing_title', 'check_in', 'check_out')