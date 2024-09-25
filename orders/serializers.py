from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import OrderItem, Order, Product, Client


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'client_name', 'client_phone', 'client_email']


class OrderSerializer(ModelSerializer):
    client = ClientSerializer(read_only=True)

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
            'item_status',
            'priority_level',
        ]
        read_only_fields = ['id', 'order', 'product', 'order_id', 'product_id']
