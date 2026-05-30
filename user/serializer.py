


from tabnanny import verbose
import token

from rest_framework import serializers
from django.core import validators

import merchant

class UserPinCodeSerializer(serializers.Serializer):
    pin_code =serializers.CharField(max_length=4, validators=[validators.RegexValidator(regex=r'^\d{4}$')], required=True, help_text="A 4-digit pin code")
    merchant_id = serializers.CharField(max_length=255, required=True, help_text="Merchant ID associated with the user")


class UserSerializer(serializers.Serializer):
    id =serializers.CharField( help_text="Unique identifier for the user")
    first_name = serializers.CharField(max_length=150, required=True, help_text="First name of the user")
    last_name = serializers.CharField(max_length=150, required=True, help_text="Last name of the user")
    token = serializers.CharField(max_length=512,  help_text="Authentication token for the user")
    refresh_token = serializers.CharField(max_length=512,  help_text="Refresh token for the user")   


class UserRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=512)
    user_id = serializers.CharField(max_length=255,help_text="")