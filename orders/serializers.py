from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        StringRelatedField,
                                        SerializerMethodField,
                                        )
from .models import OrderItem, Order, Product, Client, ComponentFinish
from products.models import OptionValue, FinishOption


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'client_name', 'client_phone', 'client_email']


class OptionValueSerializer(ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ['id', 'option', 'value']


class FinishOptionSerializer(ModelSerializer):
    finish = StringRelatedField()

    class Meta:
        model = FinishOption
        fields = ['id', 'finish', 'name']


class ComponentFinishSerializer(ModelSerializer):
    component = StringRelatedField()
    finish_option = FinishOptionSerializer(read_only=True)
    component_finish_display = SerializerMethodField()

    class Meta:
        model = ComponentFinish
        fields = ['id', 'component', 'finish_option',
                  'component_finish_display']

    def get_component_finish_display(self, obj):
        return f"{obj.component} - {obj.finish_option.name}"


class SummaryOrderSerializer(ModelSerializer):
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'order_status', 'paid']


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']


class OrderItemSerializer(ModelSerializer):
    order = SummaryOrderSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    option_values = OptionValueSerializer(many=True, read_only=True)
    product_finish = FinishOptionSerializer(read_only=True)
    item_component_finishes = ComponentFinishSerializer(
        many=True, read_only=True)
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
    option_value_id = PrimaryKeyRelatedField(
        queryset=OptionValue.objects.all(),
        source='option_values',
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
            'option_value_id',
            'option_values',
            'product_finish',
            'item_component_finishes',
            'item_value',
            'item_status',
            'priority_level',
        ]
        read_only_fields = ['id', 'order', 'product', 'order_id', 'product_id',
                            'option_values', 'product_finish',
                            'option_value_id', 'item_value',
                            'item_component_finishes',]

    # customise update to ensure the related order status is also updated
    def update(self, instance, validated_data):
        # Update the OrderItem instance
        instance = super().update(instance, validated_data)

        # After updating the OrderItem,
        # call update_order_status on the associated Order
        order = instance.order
        order.update_order_status()
        # Since update_order_status saves the order, no need to save again

        return instance


class OrderSerializer(ModelSerializer):
    client = ClientSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'discount', 'deposit', 'order_value',
                  'order_status', 'paid', 'created_on', 'updated_on',
                  'items']
