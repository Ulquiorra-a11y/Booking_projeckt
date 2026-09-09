from rest_framework import serializers

from apps.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Listing
        fields = ('id','title','description','country','city','street','house_number','rooms','max_guests','owner_name',
                  'created_at', 'price')
        read_only_fields = ('id','created_at')

    def get_owner_name(self,obj):
        return f'{obj.owner.last_name} {obj.owner.first_name}'
