
from django.db import models
from django.conf import settings
from product.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELED = 'canceled', 'Canceled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders' ,verbose_name='User')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING , verbose_name='Status')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0 , verbose_name='Subtotal')
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0,verbose_name='ShippingCost')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0 ,verbose_name='TotalAmount')
    payment_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name='PaymentRef')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True ,verbose_name='CreatedAt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='UpdatedAt')
    


    def __str__(self):
        return f'Order #{self.pk} - {self.user}'

    class Meta:
        db_table = 'order'

        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT , related_name='items')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price = models.DecimalField(max_digits=12, decimal_places=2,  verbose_name='Price')
    total_price = models.DecimalField(max_digits=12, decimal_places=2 , verbose_name='TotalPrice')

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} x {self.quantity}'

