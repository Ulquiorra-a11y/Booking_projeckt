from django.core.exceptions import ValidationError as ValidationErrorCore
from rest_framework import serializers

from apps.users.models import Customer
from core.validators import validate_birth_date


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id','deleted_at','created_at','updated_at')

class CustomerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name','last_name')

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name', 'birth_date', 'phone_number')


class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Customer
        fields = ('email', 'password', 'first_name', 'last_name', 'birth_date', 'phone_number')

    def validate_birth_date(self, value):
        if value is None:
            return value
        try:
            validate_birth_date(value)
        except ValidationErrorCore as e:
            raise serializers.ValidationError(e)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return Customer.objects.create_user(password=password, **validated_data)