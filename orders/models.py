from django.db import models
from accounts.models import User
from django.utils import timezone

# Create your models here.
class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(assigned_to__is_procurement_officer=True)

class Order(models.Model):
    objects = OrderManager()  
    product = models.CharField(max_length=255)
    unit = models.CharField(max_length=255, blank=True)
    quantity = models.FloatField()
    #total_price = models.FloatField()
    selling_price = models.FloatField(null=True, blank=True)
    cost_price = models.FloatField(null=True, blank=True)
    quantity_bought = models.FloatField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='orders/', blank=True)
    created_at = models.DateTimeField(default=timezone.now)


    # def __str__(self):
    #     return f"{self.product} - {self.quantity}{self.get_unit_display()} (to {self.assigned_to.username})"


    def __str__(self):
        return f"{self.product} - {self.quantity}kg (to {self.assigned_to.username})"