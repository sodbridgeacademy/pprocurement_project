# Generated by Django 5.0.3 on 2024-03-22 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0008_alter_order_assigned_to"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="quantity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]