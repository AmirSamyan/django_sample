# Generated manually for merchant-scoped catalog fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0003_category_merchant"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="title",
            field=models.CharField(max_length=100, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=100, verbose_name="slug"),
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("merchant", "slug"), name="uq_category_merchant_slug"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="merchant.merchant",
                verbose_name="merchant",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["merchant", "is_active"], name="ix_product_merchant_active"),
        ),
    ]
