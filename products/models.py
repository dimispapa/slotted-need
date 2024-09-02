from django.db import models
from django.core.validators import MinValueValidator


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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} | €{self.unit_cost} per {self.measurement_unit}"


# Create Product model class as the main parent model
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=7,
                                     decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
    components = models.ManyToManyField(Component, through='ProductComponent')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} | Base price at €{self.base_price}"


# Create a ProductComponent intermediary model to link the Product with its
# componets and to be able to define a quantity of each component that make up
# the product
class ProductComponent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return (f"{self.product.name} - {self.component.name} "
                f"x ({self.quantity})")


# Create an Option model to define the options for a product config that can
# be created along with a product
class Option(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, related_name='options',
                                on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class OptionValue(models.Model):
    option = models.ForeignKey(Option, related_name='values',
                               on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.option.name}: {self.value}"
