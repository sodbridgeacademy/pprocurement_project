# Generated by Django 5.0.3 on 2024-03-23 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0012_alter_order_procurement_officer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="quantity_bought",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
