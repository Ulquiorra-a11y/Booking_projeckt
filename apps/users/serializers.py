from rest_framework import serializers

from apps.users.models import Customer


class CustomerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name','last_name')

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'email', 'first_name', 'last_name', 'birth_date', 'phone_number', 'created_at')
        read_only_fields = ('id', 'email', 'created_at')

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Customer
        fields = ('email', 'password', 'first_name', 'last_name', 'birth_date', 'phone_number')

    def create(self, validated_data):
        password = validated_data.pop('password')
        return Customer.objects.create_user(password=password, **validated_data)