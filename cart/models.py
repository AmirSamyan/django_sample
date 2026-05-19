# Create your models here.
from django.conf import settings
from django.db import models

from product.models import Product


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="User",
    )
    is_active = models.BooleanField(default=True, verbose_name="IsActive")


    created_at = models.DateTimeField(auto_now_add=True, verbose_name="CreatedAt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="UpdatedAt")

    class Meta:
        db_table = "cart"
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Cart",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name="Product",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")

    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Price")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="TotalPrice")

    def save(self, *args, **kwargs):
        self.price = getattr(self.product, "price", self.price)
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    class Meta:
        db_table = "cart_item"
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"
        unique_together = ("cart", "product")  # برای اینکه هر محصول داخل یک cart تکراری نباشه

    def __str__(self):
        return f"{self.product} x {self.quantity}"
