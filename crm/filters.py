import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")   # case-insensitive search
    email = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter()         # filter by date range

    class Meta:
        model = Customer
        fields = ["name", "email", "created_at"]


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    price = django_filters.RangeFilter()       # filter by price range
    stock = django_filters.RangeFilter()       # filter by stock range

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    order_date = django_filters.DateFromToRangeFilter()
    total_amount = django_filters.RangeFilter()
    customer__name = django_filters.CharFilter(lookup_expr="icontains")  # filter by customer name

    class Meta:
        model = Order
        fields = ["order_date", "total_amount", "customer__name"]
