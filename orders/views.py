from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import generics
from .models import Order
from accounts.models import User 
from django.http import HttpResponse
from .serializers import OrderFileUploadSerializer, OrderSerializer, OrderEditSerializer
import re
import csv



# views here

class OrderFileUploadAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        print(f"file found: {file}")
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     with open(file_path, 'r') as file:
        #         orders = self.parse_csv_file(file)
        # except FileNotFoundError:
        #     return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({'error': f'Failed to read file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the CSV file
        orders = self.parse_csv_file(file)
        if not orders:
            return Response({'error': 'Failed to parse CSV file'}, status=status.HTTP_400_BAD_REQUEST)

        # Create orders for each procurement officer
        for order_data in orders:
            procurement_officer_name = order_data.get('procurement_officer')
            procurement_officer = User.objects.filter(username=procurement_officer_name).first()
            if not procurement_officer:
                continue  # Skip if procurement officer not found

            # Assign the procurement officer to the order data
            order_data['assigned_to'] = procurement_officer.id

            # Create order object directly
            Order.objects.create(**order_data)

        return Response({'success': 'Orders created successfully'}, status=status.HTTP_201_CREATED)

    def parse_csv_file(self, file):
        orders = []
        try:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean up price value
                price = self.clean_price(row['Price'])
                # Extract numeric quantity
                quantity = float(row['Quantity'].split()[0])
                orders.append({
                    'product': row['Product'],
                    'quantity': quantity,
                    'selling_price': price,
                    'procurement_officer': row['Procurement Officer'],
                    'created_at': timezone.now()  # Add current timestamp
                })
        except Exception as e:
            print(e)  # Log the error
        return orders

    def clean_price(self, price_str):
        # Remove non-numeric characters and symbols from the price string
        cleaned_price = re.sub(r'[^\d.]', '', price_str)
        # Convert the cleaned price to a float
        return float(cleaned_price)




class OrdersFileUploadAPIView(APIView):
    def post(self, request):
        serializer = OrderFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                # Read the contents of the uploaded file
                file_content = file.read().decode('utf-8')

                # Split the file content into lines
                lines = file_content.split('\n')

                # Iterate over each line and process the order information
                for line in lines:
                    # Extract procurement officer name from the line
                    match = re.match(r'^=+ (.+) =+$', line)
                    if match:
                        procurement_officer_name = match.group(1).strip()
                        # Query the database to find the user by name
                        procurement_officer = User.objects.filter(username=procurement_officer_name).first()
                        if procurement_officer:
                            # Process orders for this procurement officer
                            continue  # You can handle order processing here
                        else:
                            return Response({'error': f'Procurement officer "{procurement_officer_name}" not found'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'success': 'File uploaded successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderssFileUploadAPIView(APIView):
    def post(self, request):
        serializer = OrderFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                # Read the contents of the uploaded file
                file_content = file.read().decode('utf-8')

                # Split the file content into lines
                lines = file_content.split('\n')
                #print(f"lines here: {lines}")

                # Iterate over each line and process the order information
                for line in lines:
                    print(f"Line in the loop: {line}")
                    # Extract procurement officer name from the line
                    match = re.match(r'^=+\s* (.*?)\s*=+$', line)
                    #match = re.match(r'^=+\s*(.*?)\s*=?+$', line)
                    print(f"match found: {match}")
                    if match:
                        procurement_officer_name = match.group(1).strip()
                        print(f"officer name: {procurement_officer_name}")
                        # Query the database to find the user by name
                        procurement_officer = User.objects.filter(username=procurement_officer_name).first()
                        if procurement_officer:
                            # Create an Order object and assign the procurement officer
                            order = Order(assigned_to=procurement_officer)

                            # Parse the order details from the line
                            order_details = self.parse_order_details(line)
                            if order_details:
                                order.product = order_details.get('product', '')
                                order.unit = order_details.get('unit', '')
                                order.quantity = order_details.get('quantity', 0)
                                order.selling_price = order_details.get('selling_price')
                                order.cost_price = order_details.get('cost_price')
                                order.quantity_bought = order_details.get('quantity_bought', 0)

                                # Save the Order object to the database
                                order.save()
                            else:
                                # Handle invalid order details
                                return Response({'error': 'Invalid order details'}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'error': f'Procurement officer "{procurement_officer_name}" not found'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'success': 'File uploaded successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def parse_order_details(self, line):
        # Implement parsing logic to extract order details from the line
        # For example, you can split the line by '===>' and extract relevant information
        # Return a dictionary containing the parsed order details
        # Example parsing logic:
        parts = line.split('==>')
        if len(parts) >= 2:
            product_info = parts[0].strip()
            quantity_info = parts[1].strip()
            # Extract product name, quantity, etc. from product_info and quantity_info
            # Example:
            product_name = product_info.split('(')[0].strip()
            quantity = float(quantity_info.split()[0].strip())
            # Add additional parsing logic as needed
            return {
                'product': product_name,
                'quantity': quantity,
                # Add other fields here
            }
        else:
            return None


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
        response['Content-Disposition'] = 'attachment; filename="updated_orders_with_profit.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Unit', 'Quantity', 'Selling Price', 'Cost Price', 'Quantity Bought', 'Assigned To', 'Created At', 'Profit'])

        for order in orders:
            profit = order.cost_price - order.selling_price
            writer.writerow([
                order.product,
                order.unit,
                order.quantity,
                order.selling_price,
                order.cost_price,
                order.quantity_bought,
                order.assigned_to.username,
                order.created_at,
                profit
            ])

        return response

