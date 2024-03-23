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
    quantity = models.CharField(null=True, blank=True, max_length=255)
    selling_price = models.FloatField(null=True, blank=True)
    cost_price = models.FloatField(null=True, blank=True)
    quantity_bought = models.CharField(max_length=255, null=True, blank=True)
    profit = models.FloatField(null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders_assigned',)
    procurement_officer = models.CharField(max_length=255, blank=True, null=True)
    uploaded_file = models.FileField(upload_to='orders/', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.product} - {self.quantity} (to {self.assigned_to.username})"