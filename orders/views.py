from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models.signals import post_save
from .signals import file_uploaded
from django.db.models.signals import post_save

from .models import Order
from .serializers import OrderSerializer


# views code here

# def parse_and_create_orders(sender, uploaded_file_path, **kwargs):
#     # Access the uploaded file using the file path
#     with open(uploaded_file_path, 'r') as uploaded_file:
#         orders = ... (your existing parsing logic using uploaded_file)

#     # Create orders and handle errors
#     for order_data in orders:
#         serializer = OrderSerializer(data=order_data)
#         serializer.is_valid(raise_exception=True)
#         order = serializer.save()
#         print(f"Created Order: {order.product} - {order.quantity}kg (to {order.assigned_to.username}) - {order.created_at}")

# # Connect the signal receiver
# post_save.connect(parse_and_create_orders, sender=file_uploaded)


# class UploadOrderFileView(APIView):
#     parser_classes = [FileUploadParser]

#     def post(self, request):
#         # Get the uploaded file
#         uploaded_file = request.FILES['file']

#         # Parse the uploaded file content
#         orders = self.parse_uploaded_file(uploaded_file)

#         # Check if any orders were parsed
#         if not orders:
#             return Response({'error': 'No orders found in the uploaded file'}, status=status.HTTP_400_BAD_REQUEST)

#         # Save parsed orders to database
#         for order_data in orders:
#             serializer = OrderSerializer(data=order_data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#         return Response({'message': 'Orders uploaded successfully'}, status=status.HTTP_201_CREATED)

#     def parse_uploaded_file(self, uploaded_file):
#         orders = []
#         officer_name = None

#         for line in uploaded_file.readlines():
#             line = line.decode('utf-8').strip()

#             # Check for officer separator
#             if line.startswith('====='):
#                 officer_name = line.strip('=')
#                 continue

#             # Skip empty lines
#             if not line:
#                 continue

#             # Extract order details (assuming specific format)
#             product, quantity_str, *_ = line.split('===>')
#             quantity = float(quantity_str.split('kg')[0])
#             price_str, *_ = line.split('₦')
#             total_price = float(price_str.strip())

#             # Get the user object based on officer name
#             try:
#                 assigned_to = User.objects.get(username=officer_name, is_procurement_officer=True)
#             except User.DoesNotExist:
#                 return Response({'error': f"Procurement Officer '{officer_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

#             # Create order object with parsed data and assigned user
#             orders.append({
#                 'product': product,
#                 'quantity': quantity,
#                 'total_price': total_price,
#                 'assigned_to': assigned_to,
#             })

#         return orders


# class UploadOrderFileAdminView(UploadOrderFileView):
#     def post(self, request):
#         uploaded_file = request.FILES['file']

#         # Check for valid text file format
#         if uploaded_file.content_type != 'text/plain':
#             messages.error(request, 'Invalid file format. Please upload a text file.')
#             return redirect('admin:index')  # Redirect to admin homepage

#         # Process the file (reuse existing logic)
#         orders = self.parse_uploaded_file(uploaded_file)

#         # Save orders to database
#         for order_data in orders:
#             serializer = OrderSerializer(data=order_data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#         messages.success(request, f'Orders uploaded successfully: {len(orders)}')
#         return redirect('admin:index')