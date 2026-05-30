# Generated manually for initial inventory schema

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("merchant", "0004_alter_merchant_code_alter_merchant_phone"),
        ("product", "0003_category_merchant"),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "merchant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="locations",
                        to="merchant.merchant",
                    ),
                ),
            ],
            options={
                "db_table": "location",
            },
        ),
        migrations.CreateModel(
            name="StockItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("on_hand", models.IntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_items",
                        to="inventory.location",
                    ),
                ),
                (
                    "merchant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_items",
                        to="merchant.merchant",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stock_items",
                        to="product.product",
                    ),
                ),
            ],
            options={
                "db_table": "stock_item",
            },
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("qty_delta", models.IntegerField()),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("sale", "Sale"),
                            ("cancel", "Cancel"),
                            ("refund", "Refund"),
                            ("adjustment", "Adjustment"),
                            ("receipt", "Receipt"),
                        ],
                        max_length=20,
                    ),
                ),
                ("ref_type", models.CharField(blank=True, max_length=40, null=True)),
                ("ref_id", models.CharField(blank=True, max_length=64, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_movements",
                        to="inventory.location",
                    ),
                ),
                (
                    "merchant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_movements",
                        to="merchant.merchant",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stock_movements",
                        to="product.product",
                    ),
                ),
            ],
            options={
                "db_table": "stock_movement",
            },
        ),
        migrations.AddConstraint(
            model_name="location",
            constraint=models.UniqueConstraint(
                fields=("merchant", "name"), name="uq_location_merchant_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="stockitem",
            constraint=models.UniqueConstraint(
                fields=("merchant", "location", "product"),
                name="uq_stock_item_merchant_location_product",
            ),
        ),
        migrations.AddIndex(
            model_name="stockmovement",
            index=models.Index(fields=["merchant", "created_at"], name="ix_stock_mv_merchant_created"),
        ),
        migrations.AddIndex(
            model_name="stockmovement",
            index=models.Index(fields=["merchant", "product"], name="ix_stock_mv_merchant_product"),
        ),
    ]
