from django.contrib import admin
from .models import Client, Order, OrderItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_phone',
                    'client_email', 'created_on')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0
        filter_horizontal = ['option_values', 'finish_options']

    list_display = ('order_number', 'client', 'order_value',
                    'order_status', 'created_on',
                    'updated_on')

    # render the order number from the primary key
    def order_number(self, obj):
        return f"Order#{obj.pk}"  # Format the order number as "Order#pk"

    inlines = [OrderItemInline, ]
    search_fields = ['client_name', 'client_email']
    list_filter = ('created_on',)
