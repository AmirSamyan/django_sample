import email
from django.core import validators
from rest_framework import serializers

class MerchantCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(min_length=11, max_length=11, validators=[validators.RegexValidator(regex=r'^09\d{9}$', message='Phone number must be 11 digits')])
    password = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)


class MerchantSerializer(serializers.Serializer):
    merchant_id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255 ,read_only=True)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True,read_only=True)


class MerchantOtpSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6 ,min_length=6)
    merchant_id = serializers.CharField()

class MerchantOtpResendSerializer(serializers.Serializer):
    
    merchant_id = serializers.CharField()