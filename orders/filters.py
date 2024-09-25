import django_filters
from django.db.models import Q
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

    design_options = django_filters.CharFilter(
        method='filter_option_values')

    product_finish = django_filters.CharFilter(
        field_name='product_finish__name',
        lookup_expr='icontains')

    component_finishes = django_filters.CharFilter(
        method='filter_component_finishes')

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
            'design_options',
            'product_finish',
            'component_finishes',
            'price_min',
            'price_max',
            'item_status',
            'priority_level',
            'payment_status'
        ]

    def filter_option_values(self, queryset, name, value):
        """
        Filters OrderItems based on option_values, case-insensitive.
        Expects 'value' as a comma-separated string of option values.
        """
        # Split the input into a list of values
        values = [v.strip() for v in value.split(',') if v.strip()]

        if not values:
            return queryset

        # Initialize an empty Q object
        q_objects = Q()

        # Build Q objects for each value using __iexact
        for val in values:
            q_objects |= Q(option_values__value__iexact=val)

        # Apply the Q object to filter the queryset
        return queryset.filter(q_objects).distinct()

    def filter_component_finishes(self, queryset, name, value):
        """
        Filters OrderItems based on item_component_finishes, case-insensitive.
        Expects 'value' as a comma-separated string of finish option names.
        """
        # Split the input into a list of values
        values = [v.strip() for v in value.split(',') if v.strip()]

        if not values:
            return queryset

        # Initialize an empty Q object
        q_objects = Q()

        # Build Q objects for each value using __iexact
        for val in values:
            q_objects |= Q(
                item_component_finishes__finish_option__name__iexact=val)

        # Apply the Q object to filter the queryset
        return queryset.filter(q_objects).distinct()
