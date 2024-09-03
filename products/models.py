from django.db import models
from django.core.validators import MinValueValidator


class Finish(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        # Define the plural correctly
        verbose_name_plural = 'Finishes'
        ordering = ["name"]

    def __str__(self):
        return self.name


class FinishOption(models.Model):
    finish = models.ForeignKey(Finish, related_name='options',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.finish.name} - {self.name}"


# Create Product model class as the main parent model
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=7,
                                     decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
    finishes = models.ManyToManyField(Finish, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} | Base price at €{self.base_price}"


# Create an Option model to define the options for a product config that can
# be created along with a product
class Option(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(Product, related_name='options',
                                on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# Create the OptionValue model that defines the options for an Option model
class OptionValue(models.Model):
    option = models.ForeignKey(Option, related_name='values',
                               on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.option.name}: {self.value}"


# Create a Component model class as related class to Product model
class Component(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    finishes = models.ManyToManyField(Finish, blank=True)
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


# Create a ProductComponent intermediary model to link the Product with its
# componets and to be able to define a quantity of each component that make up
# the product
class ProductComponent(models.Model):
    option_value = models.ForeignKey(OptionValue, related_name='components',
                                     on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return (f"{self.option_value.value} - "
                f"{self.component.name} (x{self.quantity})")
