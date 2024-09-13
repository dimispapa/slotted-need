import nested_admin
from django.contrib import admin
from .models import (Product, Option, OptionValue, Component, Finish,
                     FinishOption, ProductComponent, ComponentPart)


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

    list_display = ('name', 'slug', 'description', 'base_price',)
    inlines = [OptionInline, ProductComponentInline, ]
    # Allows for the selection of multiple finishes
    filter_horizontal = ['finishes',]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


# Define the ComponentAdmin page to add components
@admin.register(Component)
class ComponentAdmin(nested_admin.NestedModelAdmin):

    # define component part inline
    class ComponentPartInLine(nested_admin.NestedStackedInline):
        model = ComponentPart
        extra = 0
        prepopulated_fields = {'slug': ('name',)}

    list_display = ('name', 'description', 'unit_cost', 'supplier_details', )
    inlines = [ComponentPartInLine, ]
    # Allows for the selection of multiple finishes
    filter_horizontal = ['finishes',]
    search_fields = ['name', 'description', 'supplier_details']
    list_filter = ('supplier_details', )
    prepopulated_fields = {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        # Save the Component object first
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Save the related ComponentParts after saving the Component
        super().save_related(request, form, formsets, change)
        # Recalculate unit cost for the component
        obj = form.instance  # Get the Component instance
        obj.calculate_unit_cost()
        obj.save()


@admin.register(Finish)
class FinishAdmin(nested_admin.NestedModelAdmin):

    class FinishOptionInline(nested_admin.NestedStackedInline):
        model = FinishOption
        extra = 0

    list_display = ['name']
    search_fields = ['name']
    inlines = [FinishOptionInline,]
