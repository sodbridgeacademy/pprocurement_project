from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Order
        fields = '__all__'


class OrderFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class OrderEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity_bought', 'cost_price', 'profit']