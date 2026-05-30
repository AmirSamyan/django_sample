from django.db import models

from merchant.models import Merchant
from product.models import Product


class Location(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "location"
        constraints = [
            models.UniqueConstraint(fields=["merchant", "name"], name="uq_location_merchant_name"),
        ]

    def __str__(self) -> str:
        return f"{self.merchant_id}:{self.name}"


class StockItem(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="stock_items")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="stock_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_items")
    on_hand = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock_item"
        constraints = [
            models.UniqueConstraint(
                fields=["merchant", "location", "product"],
                name="uq_stock_item_merchant_location_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.merchant_id}:{self.location_id}:{self.product_id}={self.on_hand}"


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        SALE = "sale", "Sale"
        CANCEL = "cancel", "Cancel"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"
        RECEIPT = "receipt", "Receipt"

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="stock_movements")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="stock_movements")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    qty_delta = models.IntegerField()
    reason = models.CharField(max_length=20, choices=Reason.choices)
    ref_type = models.CharField(max_length=40, blank=True, null=True)
    ref_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stock_movement"
        indexes = [
            models.Index(fields=["merchant", "created_at"], name="ix_stock_mv_merchant_created"),
            models.Index(fields=["merchant", "product"], name="ix_stock_mv_merchant_product"),
        ]

    def __str__(self) -> str:
        return f"{self.merchant_id}:{self.reason}:{self.product_id}:{self.qty_delta}"
