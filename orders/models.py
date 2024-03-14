from django.db import models
from accounts.models import User

# Create your models here.
class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(assigned_to__is_procurement_officer=True)

class Order(models.Model):
    objects = OrderManager()  
    product = models.CharField(max_length=255)
    quantity = models.FloatField()
    total_price = models.FloatField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} - {self.quantity}kg (to {self.assigned_to.username})"