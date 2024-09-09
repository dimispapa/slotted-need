from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product, OptionValue, FinishOption


class Client(models.Model):
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20)
    client_email = models.EmailField()
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name}"


class Order(models.Model):
    client = models.ForeignKey(Client, related_name='orders',
                               on_delete=models.SET_NULL,
                               blank=True, null=True)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    # create a status mapping to use as choices for order_status
    STATUS = {1: 'Not Started',
              2: 'In Progress',
              3: 'Made',
              4: 'Delivered'}
    order_status = models.IntegerField(
        choices=STATUS,
        default=1
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        # Sum the discount and order_value from all OrderItems
        items = self.items.all()
        self.discount = sum(item.discount * item.quantity for item in items)
        self.order_value = sum(item.item_value for item in items)
        self.save()

    def save(self, *args, **kwargs):
        # Call the method to calculate totals before saving
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Order #{self.id} by {self.client.client_name} "
                f"- Order value: €{self.order_value}")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items',
                                on_delete=models.CASCADE)
    base_price = models.DecimalField(max_digits=10, decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
    discount = models.DecimalField(max_digits=10, decimal_places=2,
                                   validators=[MinValueValidator(0.00)],
                                   default=0.00, blank=True, null=True)
    item_value = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    option_values = models.ManyToManyField(OptionValue,
                                           related_name='order_items')
    finish_options = models.ManyToManyField(FinishOption, blank=True)

    def save(self, *args, **kwargs):
        # Automatically calculate item_value before saving
        self.item_value = (self.base_price - self.discount) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}: €{self.item_value}"
