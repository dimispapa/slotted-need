from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import OrderItem, Order, Product


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'client', 'paid', 'created_on']


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']


class OrderItemSerializer(ModelSerializer):
    order = OrderSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    order_id = PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True
    )
    product_id = PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'order_id',
            'product_id',
            'item_value',
            'option_values',
            'product_finish',
            'item_component_finishes',
            'item_status',
            'priority_level',
            'paid',
        ]
        read_only_fields = ['id', 'order', 'product', 'order_id', 'product_id']
