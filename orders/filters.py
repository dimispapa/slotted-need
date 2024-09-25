import django_filters
from .models import OrderItem, Order


class OrderItemFilter(django_filters.FilterSet):

    id = django_filters.NumberFilter(
        field_name='id',
        lookup_expr='exact')

    order_id = django_filters.NumberFilter(
        field_name='order__id',
        lookup_expr='exact')

    client_name = django_filters.CharFilter(
        field_name='order__client__client_name',
        lookup_expr='icontains')

    product = django_filters.CharFilter(
        field_name='product__name',
        lookup_expr='icontains')

    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte')

    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte')

    item_status = django_filters.ChoiceFilter(
        field_name='item_status',
        choices=OrderItem.STATUS_CHOICES)

    priority_level = django_filters.ChoiceFilter(
        field_name='priority_level',
        choices=OrderItem.PRIORITY_CHOICES)

    payment_status = django_filters.ChoiceFilter(
        field_name='order__paid',
        choices=Order.PAID_CHOICES)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order_id',
            'client_name',
            'product',
            'price_min',
            'price_max',
            'item_status',
            'priority_level',
            'payment_status'
        ]
