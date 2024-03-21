import os
import sys

# Adjust Python path to include the project directory
sys.path.append('/path/to/procurement_project')  # Replace this with the actual path to your project directory

# Set DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurement_project.settings')

# Import Django modules after setting up environment
import django
from django.conf import settings

# Initialize Django
django.setup()



from django.contrib.auth.models import User
from django.utils import timezone
from orders.models import Order

# Sample order_data object
order_data = [
    {
        'procurement_officer': 'OFFICE',
        'product': 'Sample Product 1',
        'quantity': 5,
        'selling_price': 100.00,
        'quantity_bought': None,
        'cost_price': None,
        'profit': None,
    },
    {
        'procurement_officer': 'JaneDoe',
        'product': 'Sample Product 2',
        'quantity': 10,
        'selling_price': 200.00,
        'quantity_bought': None,
        'cost_price': None,
        'profit': None,
    }
]

# Iterate over order_data and create orders
for data in order_data:
    procurement_officer_name = data.get('procurement_officer')
    procurement_officer, created = User.objects.get_or_create(
        username=procurement_officer_name,
        defaults={
            'email': f"{procurement_officer_name}@example.com",
            'password': '12345678',
            'is_procurement_officer': True,  
        }
    )
    if procurement_officer:
        data['assigned_to'] = procurement_officer
    else:
        procurement_officer = User.objects.get_or_create(username='unknown_officer')[0]
        data['assigned_to'] = procurement_officer
    # Remove procurement_officer from data dictionary before creating Order
    del data['procurement_officer']
    Order.objects.create(**data)

# Verify orders
orders = Order.objects.all()
for order in orders:
    print(order)
