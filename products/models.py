from django.db import models
from django.core.validators import MinValueValidator


class Finish(models.Model):
    name = models.CharField(max_length=50)
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


# Create a ComponentPart model class for defining the lowest granular level of
# parts that make up a complete Component

class ComponentPart(models.Model):
    """Represents the most granular parts of a component."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=7, decimal_places=2,
                                    validators=[MinValueValidator(0.00)],
                                    blank=True, null=True)
    component = models.ForeignKey('Component', related_name='parts',
                                  on_delete=models.CASCADE)
    # How many parts make up a complete component
    quantity = models.PositiveIntegerField(default=1,
                                           validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} x {self.quantity} | @ €{self.unit_cost}"


# Create a Component model class as related class to Product model
class Component(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=7, decimal_places=2,
                                    validators=[MinValueValidator(0.00)],
                                    blank=True, null=True)
    supplier_details = models.TextField(blank=True, null=True)
    finishes = models.ManyToManyField(Finish, blank=True,
                                      related_name='components')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        # Get the component parts if they exist
        parts = self.parts.all()
        if parts.exists():
            parts_str = ', '.join(
                [f"{part.name} (x{part.quantity})" for part in parts]
            )
            return f"{self.name} @ €{self.unit_cost} | Parts: {parts_str}"
        return f"{self.name} @ €{self.unit_cost}"

    def calculate_unit_cost(self):
        """
        If the component has parts, calculate the total unit cost as the sum
        of the unit costs of its parts multiplied by the quantity of each part.
        """
        parts = self.parts.all()
        if parts.exists():
            total_cost = 0
            for part in parts:
                if part.unit_cost is not None:
                    total_cost += part.unit_cost * part.quantity
            self.unit_cost = total_cost if total_cost > 0 else None
        return self.unit_cost

    def save(self, *args, **kwargs):
        """
        Ensures unit cost is calculated and updated after related
        ComponentPart objects are saved.
        """
        # Save the Component first to ensure it has a primary key
        super().save(*args, **kwargs)

        # Calculate the unit cost after saving the related parts
        self.calculate_unit_cost()

        # Save again after calculating unit cost
        super().save(*args, **kwargs)


# Create Product model class as the main parent model
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=7,
                                     decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
    components = models.ManyToManyField(Component, through="ProductComponent",
                                        related_name='products')
    finishes = models.ManyToManyField(Finish, blank=True,
                                      related_name='products')

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
        return f"{self.name}"


# Create the OptionValue model that defines the options for an Option model
class OptionValue(models.Model):
    option = models.ForeignKey(Option, related_name='values',
                               on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.value}"


# Create a ProductComponent intermediary model to link the Product with its
# components in the many-to-many relationship and to be able to define a
# quantity of each component that make up the product
class ProductComponent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    option_value = models.ForeignKey(OptionValue, on_delete=models.SET_NULL,
                                     blank=True, null=True,
                                     related_name='product_components')
    quantity = models.PositiveIntegerField(default=1,
                                           validators=[MinValueValidator(1)])

    def __str__(self):
        return (f"{self.component.name} (x{self.quantity})")
