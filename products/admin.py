import nested_admin
from django.contrib import admin
from .models import (Product, Option, OptionValue, Component, Finish,
                     FinishOptionValue, FinishOption, ProductComponent)


# Define inline classes to use in the admin pages
class ProductComponentInline(nested_admin.NestedTabularInline):
    model = ProductComponent
    extra = 1
    verbose_name = "Component"
    verbose_name_plural = "Components"


class OptionValueInline(nested_admin.NestedTabularInline):
    model = OptionValue
    inlines = [ProductComponentInline]
    extra = 1


class OptionInline(nested_admin.NestedStackedInline):
    model = Option
    inlines = [OptionValueInline]
    extra = 0


class FinishOptionValueInline(nested_admin.NestedTabularInline):
    model = FinishOptionValue
    extra = 1


class FinishOptionInline(nested_admin.NestedStackedInline):
    model = FinishOption
    inlines = [FinishOptionValueInline]
    extra = 0


# Define the ProductAdmin page with OptionInline to add Options in same view
@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'slug', 'description', 'base_price', 'created_on',
                    'updated_on')
    inlines = [OptionInline,]
    # Allows for the selection of multiple finishes
    filter_horizontal = ['finishes',]
    search_fields = ['name', 'description']
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('name',)}


# Define the ComponentAdmin page to add components
@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'unit_cost',
                    'measurement_unit', 'supplier_source', 'created_on',
                    'updated_on')
    search_fields = ['name', 'description', 'supplier_source']
    list_filter = ('supplier_source', 'created_on',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Finish)
class FinishAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [FinishOptionInline,]
