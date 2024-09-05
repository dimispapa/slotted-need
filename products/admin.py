import nested_admin
from django.contrib import admin
from .models import (Product, Option, OptionValue, Component, Finish,
                     FinishOption, ProductComponent)


# Define the ProductAdmin page with OptionInline to add Options in same view
@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):

    class OptionInline(nested_admin.NestedStackedInline):
        class OptionValueInline(nested_admin.NestedTabularInline):
            model = OptionValue
            extra = 0
        model = Option
        inlines = [OptionValueInline]
        extra = 0

    class ProductComponentInline(nested_admin.NestedStackedInline):
        model = ProductComponent
        extra = 0
        verbose_name = "Component"
        verbose_name_plural = "Components"

    list_display = ('name', 'slug', 'description', 'base_price',)
    inlines = [OptionInline, ProductComponentInline, ]
    # Allows for the selection of multiple finishes
    filter_horizontal = ['finishes',]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


# Define the ComponentAdmin page to add components
@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'unit_cost',
                    'measurement_unit', 'supplier_details', )
    # Allows for the selection of multiple finishes
    filter_horizontal = ['finishes',]
    search_fields = ['name', 'description', 'supplier_details']
    list_filter = ('supplier_details', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Finish)
class FinishAdmin(nested_admin.NestedModelAdmin):

    class FinishOptionInline(nested_admin.NestedStackedInline):
        model = FinishOption
        extra = 0

    list_display = ['name']
    search_fields = ['name']
    inlines = [FinishOptionInline,]
