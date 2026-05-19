from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Merchant)
class MerchantAdmin(admin.ModelAdmin):
    pass