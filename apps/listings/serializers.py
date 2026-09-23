from rest_framework import serializers

from apps.listings.models import Listing, Photos



class PhotoSerializer(serializers.ModelSerializer):
    listing_url = serializers.HyperlinkedRelatedField(
        view_name='listing-detail',source='listing',read_only=True,)
    class Meta:
        model = Photos
        fields = ('id', 'listing','listing_url', 'image', 'is_main', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['listing'].queryset = Listing.objects.filter(owner=request.user)


class PhotoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ('id', 'image', 'is_main', 'order')

class ListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField(read_only=True)
    photos = PhotoNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ('id','title','description','country','city','street','house_number','rooms','photos','max_guests',
                  'owner_name','created_at', 'price', 'average_rating')
        read_only_fields = ('id','created_at')

    def get_owner_name(self,obj):
        return f'{obj.owner.last_name} {obj.owner.first_name}'

class ListingShortUpdateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='listing-detail')
    main_photo = serializers.SerializerMethodField()
    class Meta:
        model = Listing
        fields = ('url','id','main_photo','title','description','price','average_rating')

    def get_main_photo(self, obj):
        photo = obj.photos.filter(is_main=True).first()
        if photo and self.context.get('request'):
            return self.context['request'].build_absolute_uri(photo.image.url)
        return None

