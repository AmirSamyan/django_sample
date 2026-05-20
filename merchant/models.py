
from random import randint
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.text import slugify
from django.core import validators
# Create your models here.



class Merchant(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    merchant_id = models.SlugField(max_length=255, unique=True, verbose_name="MerchantID")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", null=True ,blank=True)
    phone = models.CharField(verbose_name='PhoneNumber', default=0,max_length=11,validators=[validators.RegexValidator(regex=r'^09\d{9}$', message='Phone number must be 11 digits')])
    password = models.CharField(max_length=255, verbose_name="Password")
    code = models.CharField(verbose_name="OTP" , max_length=6,validators=[validators.RegexValidator(regex=r'^\d{6}$', message='OTP must be 6 digits')], null=True ,blank=True)
    expair_code = models.DateTimeField(blank=True, null=True, verbose_name="ExpairCode")
    used_code_at = models.DateTimeField(blank=True, null=True, verbose_name="UsedCodeAt")
    is_active = models.BooleanField(default=False, verbose_name="IsActive")
    is_approved = models.BooleanField(default=False, verbose_name="IsApproved")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="CreatedAt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="UpdatedAt")
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name="ApprovedAt")

    def save(self, *args, **kwargs):
        number = randint(1000, 9999)
        self.password = make_password(self.password)
        self.merchant_id = slugify(f"{self.name}-{number}")
        if self.is_approved :
            self.is_active = True
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "merchant"
        verbose_name = "Merchant"
        verbose_name_plural = "Merchants"
        

    def __str__(self):
        return self.name