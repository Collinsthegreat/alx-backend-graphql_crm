""" 
import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.utils import timezone

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# === GraphQL Types ===
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at", "updated_at")
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at", "updated_at")
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "products",
            "total_amount",
            "order_date",
            "created_at",
            "updated_at",
        )
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

    # ✅ Fix: return products as a list instead of a Relay connection
    products = graphene.List(lambda: ProductType)

    def resolve_products(self, info):
        return self.products.all()


# === Validators ===
def validate_phone(phone):
    if not re.match(r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$", phone):
        raise ValueError("Invalid phone format. Use +1234567890 or 123-456-7890.")


# === Input Types ===
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


# === Mutations ===
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone:
            try:
                validate_phone(phone)
            except ValueError as e:
                raise Exception(str(e))

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, customers):
        created_customers = []
        errors = []

        with transaction.atomic():
            for data in customers:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"Email {data.email} already exists")
                        continue
                    if data.phone:
                        validate_phone(data.phone)
                    cust = Customer.objects.create(
                        name=data.name,
                        email=data.email,
                        phone=data.phone or ""
                    )
                    created_customers.append(cust)
                except Exception as e:
                    errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products = []
        for pid in product_ids:
            try:
                products.append(Product.objects.get(pk=pid))
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order.objects.create(
            customer=customer,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        order.calculate_total()

        return CreateOrder(order=order)


# === Root Schema ===
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
"""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        filterset_class = CustomerFilter
        interfaces = (relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        filterset_class = ProductFilter
        interfaces = (relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        filterset_class = OrderFilter
        interfaces = (relay.Node,)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def validate_phone(phone):
        if not phone:
            return True
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return re.match(pattern, phone)

    @classmethod
    def mutate(cls, root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            return cls(customer=None, message="Email already exists")
        if input.phone and not cls.validate_phone(input.phone):
            return cls(customer=None, message="Invalid phone format")
        customer = Customer(name=input.name, email=input.email, phone=input.phone)
        customer.save()
        return cls(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, customer_data in enumerate(input):
                name = customer_data.name
                email = customer_data.email
                phone = customer_data.phone
                if not name or not email:
                    errors.append(f"Row {idx+1}: Name and email required")
                    continue
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx+1}: Email already exists")
                    continue
                if phone and not CreateCustomer.validate_phone(phone):
                    errors.append(f"Row {idx+1}: Invalid phone format")
                    continue
                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created.append(customer)
        return cls(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")
        product = Product(name=input.name, price=input.price, stock=input.stock or 0)
        product.save()
        return cls(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            return cls(order=None, message="Invalid customer ID")
        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            return cls(order=None, message="One or more product IDs are invalid")
        if not products:
            return cls(order=None, message="At least one product must be selected")
        order = Order(customer=customer, order_date=input.order_date or timezone.now())
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products])
        order.total_amount = total
        order.save()
        return cls(order=order, message="Order created successfully")

# Query class
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_all_customers(root, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(root, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(root, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs

# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
