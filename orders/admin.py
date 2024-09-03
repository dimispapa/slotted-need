from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    filter_horizontal = ['option_values', 'finishes']


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_phone',
                    'customer_email', 'created_on',
                    'updated_on')
    inlines = [OrderItemInline,]
    search_fields = ['customer_name', 'customer_email']
    list_filter = ('created_on',)
