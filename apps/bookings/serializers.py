from rest_framework import serializers

from apps.bookings.models import Booking

class BookingSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    guest_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Booking
        fields = ('id','listing','listing_title','guest_name','check_in','check_out','guests_count','status','total_price',
                  'created_at')
        read_only_fields = ('id', 'status', 'total_price', 'created_at')

    def get_guest_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}"

class BookingShortSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'listing_title', 'check_in', 'check_out')