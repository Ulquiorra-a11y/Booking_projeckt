from rest_framework import serializers

from apps.users.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id','deleted_at','created_at','updated_at')

class CustomerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name','last_name')
