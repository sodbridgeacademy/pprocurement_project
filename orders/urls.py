from django.urls import path
from .views2 import OrderFileUploadAPIView

urlpatterns = [
    path('upload/', OrderFileUploadAPIView.as_view(), name='order_file_upload'),
]
