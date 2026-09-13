from rest_framework import serializers

from apps.listings.models import Listing, Photos


class ListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Listing
        fields = ('id','title','description','country','city','street','house_number','rooms','max_guests','owner_name',
                  'created_at', 'price')
        read_only_fields = ('id','created_at')

    def get_owner_name(self,obj):
        return f'{obj.owner.last_name} {obj.owner.first_name}'

class ListingShortUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('id','title','description','price')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ('id', 'listing', 'image', 'is_main', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['listing'].queryset = Listing.objects.filter(owner=request.user)