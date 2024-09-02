from django.contrib import admin
from .models import Product, Component


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'base_price', 'created_on',
                    'updated_on')
    search_fields = ['name', 'description']
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'unit_cost',
                    'measurement_unit', 'supplier_source', 'created_on',
                    'updated_on')
    search_fields = ['name', 'description', 'supplier_source']
    list_filter = ('supplier_source', 'created_on',)
    prepopulated_fields = {'slug': ('name',)}
