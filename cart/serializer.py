from decimal import Decimal

from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import  serializers

class CartItemViewSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(read_only=True ,source='product.id')
    product_title = serializers.CharField(read_only=True ,source='product.title')
    product_description = serializers.CharField(read_only=True ,source='product.description')
    quantity = serializers.IntegerField()
    price =serializers.DecimalField(max_digits=12, decimal_places=2 ,read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2,read_only=True)

class CartItemCreateSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()





class CartViewSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    cart_items = CartItemViewSerializer(read_only=True,many=True ,source='items')
    cart_total = serializers.SerializerMethodField(read_only=True)
    @extend_schema_field(Decimal)
    def get_cart_total(self,obj):
        return sum([item.total_price for item in obj.items.all()])






class CartCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    cart_id = serializers.IntegerField(read_only=True )





