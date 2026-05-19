import email
from django.core import validators
from rest_framework import serializers

class MerchantCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.IntegerField(validators=[validators.MinLengthValidator(11), validators.MaxLengthValidator(11)])
    password = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)


class MerchantSerializer(serializers.Serializer):
    merchant_id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255 ,read_only=True)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True,read_only=True)