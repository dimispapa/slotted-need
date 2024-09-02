from django.db import models
from django.core.validators import MinValueValidator


# Create Product model class as the main parent model
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=7,
                                     decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


# Create a Component model class as related class to Product model
class Component(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=7,
                                    decimal_places=2,
                                    validators=[MinValueValidator(0.00)])
    # create a units mapping to use as choices for measurement_unit
    UNITS = {'g': 'gram',
             'kg': 'kilogram',
             'l': 'litre',
             'pc': 'piece'}
    measurement_unit = models.CharField(
        max_length=2,
        choices=UNITS,
        default='pc'
    )
    supplier_source = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
