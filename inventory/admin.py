from django.contrib import admin

from inventory.models import Location, StockItem, StockMovement


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "merchant", "name", "is_default", "is_active")
    list_filter = ("merchant", "is_default", "is_active")


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("id", "merchant", "location", "product", "on_hand", "updated_at")
    list_filter = ("merchant", "location")
    search_fields = ("product__title",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "merchant", "location", "product", "reason", "qty_delta", "created_at")
    list_filter = ("merchant", "location", "reason")
