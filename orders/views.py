from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import generics
from .models import Order
from accounts.models import User 
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from .serializers import OrderFileUploadSerializer, OrderSerializer, OrderEditSerializer
import re
import csv
import io


# views here

class OrderFileUploadAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        print(f"file found: {file}")
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            orders = self.parse_csv_file(file)
        except Exception as e:
            print(e)
            return Response({'error': f'Failed to parse CSV file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if not orders:
            return Response({'error': 'No orders found in the CSV file'}, status=status.HTTP_400_BAD_REQUEST)

        # orders found
        #print("orders in views", orders)
        print("get orders type:", type(orders))
        
        for order_data in orders:
            procurement_officer_name = order_data.get('procurement_officer')
            print(f"Officer name from file: {procurement_officer_name}")

            procurement_officer, created = User.objects.get_or_create(
                username=procurement_officer_name,
                defaults={
                    'email': f"{procurement_officer_name}@example.com",
                    'is_procurement_officer': True,  
                }
            )

            # Check if the user was created or fetched from the database
            if created:
                # Set a default password for new users
                procurement_officer.set_password('12345678')
                procurement_officer.save()
                print(f"New procurement officer '{created}' created.")
            else:
                print(f"Procurement officer '{procurement_officer_name}' found in the database.")
            
            # Save the order obj
            if procurement_officer:
                # If the procurement officer exists, assign the order to them
                order_data['procurement_officer'] = procurement_officer_name
                order_data['assigned_to'] = procurement_officer
            else:
                # Create a user for "unknown" officer or use an existing user for this purpose
                unknown_officer = User.objects.get_or_create(username='unknown_officer')[0]
                order_data['procurement_officer'] = created
                order_data['assigned_to'] = unknown_officer

            print("Before creating orders to db")
            print(f"final parsed orders {orders[:10]}")
            del order_data['procurement_officer']
            # Now, create the order
            Order.objects.create(**order_data)
        return Response({'success': 'Orders created successfully'}, status=status.HTTP_201_CREATED)

    def parse_csv_file(self, file):
        orders = []
        print("parse CSV cunc just called")
        try:
            # Open the file in text mode using io.TextIOWrapper
            file_wrapper = io.TextIOWrapper(file, encoding='utf-8')
            reader = csv.reader(file_wrapper, delimiter=',')
            next(reader)  # Skip header row
            for row in reader:
                if len(row) < 4:
                    print(f"Ignoring row: {row} - Insufficient fields")
                    continue

                procurement_officer_name = row[0]
                product = row[1]
                quantity = float(row[2].split()[0])
                price = self.clean_price(row[3])
                orders_data = {
                    'procurement_officer': procurement_officer_name,
                    'product': product,
                    'quantity': quantity,
                    'selling_price': price,
                    'quantity_bought': None,  
                    'cost_price': None,  
                    'profit': None,  
                    'assigned_to': None,  
                    'created_at': timezone.now()
                }
                orders.append(orders_data)
        except Exception as e:
            print(f"Failed to parse CSV file: {str(e)}")
        return orders


    def clean_price(self, price_str):
        # Remove non-numeric characters and symbols from the price string
        cleaned_price = re.sub(r'[^\d.]', '', price_str)
        # Convert the cleaned price to a float
        return float(cleaned_price)



class OrderListAPIView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



class OrderFilterByDateAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Get the date from the query parameters
        date_str = self.request.query_params.get('date')
        if date_str:
            # Convert the date string to a datetime object
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                return Order.objects.none()

            # Filter orders by the specified date
            queryset = Order.objects.filter(created_at__date=date)
        else:
            # If date parameter is not provided, return all orders
            queryset = Order.objects.all()

        return queryset



class ProcurementOfficerOrdersAPIView(APIView):
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(assigned_to=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



class ProcurementOfficerOrderEditAPIView(APIView):
    def patch(self, request, order_id):
        user = request.user
        try:
            order = Order.objects.get(id=order_id, assigned_to=user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderEditSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():

            # Calculate profit (not needed!)
            selling_price = order.selling_price
            cost_price = serializer.validated_data.get('cost_price')
            profit = cost_price - selling_price
            serializer.save(profit=profit)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderDownloadCSVExport(APIView):
    def get(self, request):
        orders = Order.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="updated_orders_by_procurement.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Unit', 'Quantity', 'Selling Price', 'Cost Price', 'Quantity Bought', 'Assigned To', 'Created At', 'Profit'])

        for order in orders:
            profit = order.cost_price - order.selling_price if order.cost_price is not None else None
            assigned_to_username = order.assigned_to.username if order.assigned_to else None
            created_at_formatted = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None

            writer.writerow([
                order.product,
                order.unit,
                order.quantity,
                order.selling_price,
                order.cost_price,
                order.quantity_bought,
                assigned_to_username,
                created_at_formatted,
                profit
            ])

        return response
