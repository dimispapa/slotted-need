from django.contrib import admin
from .models import Product, Component, ProductComponent


# Register your models here.
class ProductComponentInline(admin.TabularInline):
    model = ProductComponent
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'base_price', 'created_on',
                    'updated_on')
    inlines = [ProductComponentInline,]
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
