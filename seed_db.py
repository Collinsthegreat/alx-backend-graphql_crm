import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def seed():
    # Clear old data (optional)
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create some customers
    alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    bob = Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")

    # Create some products
    laptop = Product.objects.create(name="Laptop", price=999.99, stock=10)
    phone = Product.objects.create(name="Phone", price=499.99, stock=5)

    # Create an order
    order = Order.objects.create(customer=alice, order_date=datetime.now())
    order.products.set([laptop, phone])
    order.total_amount = sum([p.price for p in order.products.all()])
    order.save()

    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed()
