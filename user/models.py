
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core import validators

from django.db import models
from merchant import models as merchant_models


# Create your models here.





class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        MERCHANT_ADMIN = "merchant_admin", "Merchant Admin"
        CASHIER = "cashier", "Cashier"

    pin_code = models.CharField(max_length=4,validators=[validators.RegexValidator(regex=r'^\d{4}$')], verbose_name="Pin Code")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    merchant = models.ForeignKey(
        merchant_models.Merchant,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name="Merchant",
        blank=True,
        null=True,
    )
    groups = models.ManyToManyField(Group, related_name="groups", blank=True, verbose_name="Groups")
    user_permissions = models.ManyToManyField(Permission, related_name="user_permissions", blank=True, verbose_name="User Permissions")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
