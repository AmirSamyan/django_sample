# Generated manually for RBAC role + nullable merchant

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_user_pin_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Admin"),
                    ("merchant_admin", "Merchant Admin"),
                    ("cashier", "Cashier"),
                ],
                default="cashier",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="merchant.merchant",
                verbose_name="Merchant",
            ),
        ),
    ]
