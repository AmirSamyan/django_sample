from django.db import models
from django.utils.text import slugify

from merchant.models import Merchant

# Create your models here.


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStamp):
    title = models.CharField(max_length=100, unique=True, verbose_name='title', blank=False)
    slug = models.SlugField(max_length=100, unique=True, verbose_name='slug', blank=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name='merchant', related_name='categories',null=True, blank=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'


class Product(TimeStamp):
    title = models.CharField(max_length=200, verbose_name='title')
    description = models.TextField(verbose_name='description')
    price= models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price')
    image = models.ImageField(upload_to='product', verbose_name='image')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='category', related_name='products')
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Products'
        verbose_name = 'Product'
