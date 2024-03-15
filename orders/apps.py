from django.apps import AppConfig
from django.db.models.signals import post_save
from .signals import file_uploaded


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        from .models import Order
        post_save.connect(handle_uploaded_file, sender=Order)

def handle_uploaded_file(sender, instance, created, **kwargs):
    if created and instance.uploaded_file:
        # Get the uploaded file path
        uploaded_file_path = instance.uploaded_file.path

        # Trigger the file_uploaded signal with the file path
        file_uploaded.send(sender=sender, uploaded_file_path=uploaded_file_path)



# class OrdersConfig(AppConfig):
#     name = 'orders'

    