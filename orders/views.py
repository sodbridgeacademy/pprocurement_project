from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

from .models import Order
from .serializers import OrderSerializer

class UploadOrderFileView(APIView):
    parser_classes = [FileUploadParser]

    def post(self, request):
        # Get the uploaded file
        uploaded_file = request.FILES['file']

        # Parse the uploaded file content
        orders = self.parse_uploaded_file(uploaded_file)

        # Check if any orders were parsed
        if not orders:
            return Response({'error': 'No orders found in the uploaded file'}, status=status.HTTP_400_BAD_REQUEST)

        # Save parsed orders to database
        for order_data in orders:
            serializer = OrderSerializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'message': 'Orders uploaded successfully'}, status=status.HTTP_201_CREATED)

    def parse_uploaded_file(self, uploaded_file):
        orders = []
        officer_name = None

        for line in uploaded_file.readlines():
            line = line.decode('utf-8').strip()

            # Check for officer separator
            if line.startswith('====='):
                officer_name = line.strip('=')
                continue

            # Skip empty lines
            if not line:
                continue

            # Extract order details (assuming specific format)
            product, quantity_str, *_ = line.split('===>')
            quantity = float(quantity_str.split('kg')[0])
            price_str, *_ = line.split('₦')
            total_price = float(price_str.strip())

            # Get the user object based on officer name
            try:
                assigned_to = User.objects.get(username=officer_name, is_procurement_officer=True)
            except User.DoesNotExist:
                return Response({'error': f"Procurement Officer '{officer_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Create order object with parsed data and assigned user
            orders.append({
                'product': product,
                'quantity': quantity,
                'total_price': total_price,
                'assigned_to': assigned_to,
            })

        return orders