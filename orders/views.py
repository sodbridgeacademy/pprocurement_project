from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from .models import Order
from accounts.models import User 
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from .serializers import OrderFileUploadSerializer, OrderSerializer, OrderEditSerializer

import re
import csv
import io
import ast


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
            # Convert string to dictionary
            #order_data_dict = ast.literal_eval(order_data)
            if isinstance(order_data, dict):
                print("Order is confirmed dict!")
                procurement_officer_name = order_data.get('procurement_officer')
                #procurement_officer_name = order_data_dict.get('procurement_officer')
                print(f"Officer name from file: {procurement_officer_name}")
            else:
                print("Not a dictionary obj!!!")

            procurement_officer, created = User.objects.get_or_create(
                username=procurement_officer_name,
                defaults={
                    'email': f"{procurement_officer_name}@example.com",
                    'is_procurement_officer': True,  
                }
            )

            print(f"Officer username here: {procurement_officer_name}")

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
                #order_data['procurement_officer'] = procurement_officer_name.u
                order_data['assigned_to'] = procurement_officer
            else:
                # Create a user for "unknown" officer or use an existing user for this purpose
                unknown_officer = User.objects.get_or_create(username=procurement_officer_name)[0]
                #order_data['procurement_officer'] = created
                order_data['assigned_to'] = unknown_officer

            print("Before creating orders in db....")
            print(f"final parsed orders {orders[:10]}")
            #del order_data['procurement_officer']
            # Now, create the order
            Order.objects.create(**order_data)
        return Response({'success': 'New orders created successfully :)'}, status=status.HTTP_201_CREATED)

    def parse_csv_file(self, file):
        orders = []
        print("parse CSV func just called!")
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
                print(f"officer name to be used from file: {procurement_officer_name}")
                product = row[1]
                quantity = row[2]
                #quantity, quantity_measurement = self.extract_quantity(quantity_str)
                price = self.clean_price(row[3])
                orders_data = {
                    'product': product,
                    'quantity': quantity,
                    #'quantity': f"{quantity} {quantity_measurement}" if quantity_measurement else str(quantity),
                    'selling_price': price,
                    'procurement_officer': procurement_officer_name,
                    'quantity_bought': None,  
                    'cost_price': None,  
                    'profit': None,  
                    'assigned_to': None,  
                    'created_at': timezone.now()
                }
                orders.append(orders_data)
                print(f'orders officer: {orders[:2]}')
        except Exception as e:
            print(f"Failed to parse CSV file: {str(e)}")
        return orders


    def clean_price(self, price_str):
        # Remove non-numeric characters and symbols from the price string
        cleaned_price = re.sub(r'[^\d.]', '', price_str)
        # Convert the cleaned price to a float
        return float(cleaned_price)



class OrderListAPIView(APIView):
    #pagination_class = PageNumberPagination

    def get(self, request):
        # Get queryset for orders
        orders = Order.objects.all()

        # Paginate the queryset
        paginator = PageNumberPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)

        # Serialize paginated queryset
        serializer = OrderSerializer(paginated_orders, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)



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



class OrderFilterByDateAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_filtered_queryset(self, date_str):
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Order.objects.none()

            queryset = Order.objects.filter(created_at__date=date).order_by('id')
        else:
            queryset = Order.objects.all().order_by('id')

        return queryset

    def get_queryset(self):
        date_str = self.request.query_params.get('date')
        queryset = self.get_filtered_queryset(date_str)
        return queryset

    # def get_queryset(self):
    #     # Get the date from the query parameters
    #     date_str = self.request.query_params.get('date')
    #     if date_str:
    #         # Convert the date string to a datetime object
    #         try:
    #             date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #             print(f"stripped date here: {date}")
    #         except ValueError:
    #             # Handle invalid date format
    #             return Order.objects.none()

    #         # Filter orders by the specified date
    #         queryset = Order.objects.filter(created_at__date=date).order_by('id')
    #     else:
    #         # If date parameter is not provided, return all orders
    #         queryset = Order.objects.all().order_by('id')

    #     # Store the filtered queryset in a variable
    #     self.filtered_queryset = queryset
    #     print(f"queryset test: {queryset[:5]}")

    #     return queryset



class OrderDownloadCSVExport(APIView):
    def get(self, request):
        # Get the queryset based on the filter parameters
        # filter_view = OrderFilterByDateAPIView()
        # queryset = filter_view.get_queryset()

        # # Access the filtered queryset from the filter-by-date view
        # queryset = getattr(self, 'filtered_queryset', None)

        # # If queryset is not set, return an error response
        # if queryset is None:
        #     return Response({'error': 'Filtered queryset not found'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date')
        queryset = OrderFilterByDateAPIView.get_filtered_queryset(self, date_str)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="updated_orders_by_procurement.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Unit', 'Quantity', 'Selling Price', 'Cost Price', 'Quantity Bought', 'Assigned To', 'Created At', 'Profit'])

        for order in queryset:
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



# downloads all the orders without filter
class OrderDownloadCSVExport1(APIView):
    def get(self, request):
        orders = Order.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="updated_orders_by_procurement.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Quantity', 'Selling Price', 'Cost Price', 'Quantity Bought', 'Assigned To', 'Created At', 'Profit'])

        for order in orders:
            profit = order.selling_price - order.cost_price if order.cost_price is not None else None
            assigned_to_username = order.assigned_to.username if order.assigned_to else None
            created_at_formatted = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None

            writer.writerow([
                order.product,
                order.quantity,
                order.selling_price,
                order.cost_price,
                order.quantity_bought,
                assigned_to_username,
                created_at_formatted,
                profit
            ])

        return response
