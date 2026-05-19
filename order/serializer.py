
from rest_framework import  serializers

from django.contrib.auth import get_user_model
from order.models import Order ,OrderItem

User = get_user_model()
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'




class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['payment_ref', 'total_amount', 'status', 'shipping_cost', 'subtotal', 'created_at', 'updated_at']



class OrderPaymentSerializer(serializers.Serializer):
    user_id=serializers.IntegerField()
    notes=serializers.CharField(max_length=256)
    cart_id=serializers.IntegerField()