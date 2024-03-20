from django.urls import path
from .views import OrderFileUploadAPIView, OrderListAPIView, ProcurementOfficerOrdersAPIView, \
OrderFilterByDateAPIView, OrderDownloadCSVExport

urlpatterns = [
    path('upload-file/', OrderFileUploadAPIView.as_view(), name='order_file_upload'),
    path('all/', OrderListAPIView.as_view(), name='order-list'),
    path('my-orders/', ProcurementOfficerOrdersAPIView.as_view(), name='procurement_officer_orders'),
    path('filter-by-date/', OrderFilterByDateAPIView.as_view(), name='order_filter_by_date'),
    path('orders/profit/csv/', OrderDownloadCSVExport.as_view(), name='order-download-csv'),

]
