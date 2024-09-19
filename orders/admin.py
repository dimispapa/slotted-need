import nested_admin
from django.contrib import admin
from .models import Client, Order, OrderItem, ComponentFinish


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_phone',
                    'client_email', 'created_on')


@admin.register(Order)
class OrderAdmin(nested_admin.NestedModelAdmin):

    class OrderItemInline(nested_admin.NestedStackedInline):
        class ComponentFinishInLine(nested_admin.NestedTabularInline):
            model = ComponentFinish
            extra = 0

        filter_horizontal = ['option_values']
        model = OrderItem
        extra = 0
        inlines = [ComponentFinishInLine]

    list_display = ('order_number', 'client', 'order_value',
                    'order_status', 'created_on',
                    'updated_on')
    inlines = [OrderItemInline]
    search_fields = ['client__client_name', 'client__client_email']
    list_filter = ['created_on']

    # render the order number from the primary key
    def order_number(self, obj):
        return f"Order#{obj.pk}"  # Format the order number as "Order#pk"
