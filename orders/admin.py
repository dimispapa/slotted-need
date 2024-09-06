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
        filter_horizontal = ['option_values', 'finishes']

    list_display = ('client', 'discount',
                    'order_status', 'created_on',
                    'updated_on')
    inlines = [OrderItemInline, ]
    search_fields = ['client_name', 'client_email']
    list_filter = ('created_on',)
