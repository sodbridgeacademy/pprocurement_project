# Generated by Django 5.0.3 on 2024-03-15 05:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="order",
            name="uploaded_file",
            field=models.FileField(blank=True, upload_to="orders/"),
        ),
    ]
