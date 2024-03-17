from django.urls import path
from .views2 import OrderFileUploadAPIView, OrderListAPIView

urlpatterns = [
    path('upload/', OrderFileUploadAPIView.as_view(), name='order_file_upload'),
    path('all/', OrderListAPIView.as_view(), name='order-list'),
]
