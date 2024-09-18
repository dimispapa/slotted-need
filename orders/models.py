from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product, OptionValue, FinishOption, Component


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
        max_digits=10, decimal_places=2, default=0,
        blank=True, null=True)
    deposit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        blank=True, null=True)
    order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
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
        """Calculate the total discount and order value based
        on order items."""
        # Ensure there are items before trying to calculate totals
        items = self.items.all()
        if items.exists():  # Only calculate if there are items
            self.discount = sum(
                (item.discount or 0) * (item.quantity or 0) for item in items
            )
            self.order_value = sum(item.item_value for item in items)

    class Meta:
        ordering = ["-created_on"]

    def save(self, *args, **kwargs):
        # Only calculate totals after the object has been saved
        # and has a primary key
        if self.pk:
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
                                   blank=True, null=True)
    item_value = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    option_values = models.ManyToManyField(OptionValue,
                                           related_name='order_items',
                                           blank=True
                                           )
    product_finish = models.ForeignKey(FinishOption, on_delete=models.SET_NULL,
                                       blank=True, null=True,
                                       related_name='order_items'
                                       )

    def save(self, *args, **kwargs):
        # Ensure base_price and discount are converted from None
        base_price = self.base_price or Decimal('0.00')
        discount = self.discount or Decimal('0.00')
        # Automatically calculate item_value before saving
        self.item_value = (base_price - discount) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}: €{self.item_value}"


class ComponentFinish(models.Model):
    order_item = models.ForeignKey(OrderItem,
                                   related_name='item_component_finishes',
                                   on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    finish_option = models.ForeignKey(FinishOption, on_delete=models.CASCADE)

    class Meta:
        # Define the plural correctly
        verbose_name_plural = 'Component Finishes'

    def __str__(self):
        return (f"{self.order_item} - {self.component.name} - "
                f"{self.finish_option.name}")


class OptionFinish(models.Model):
    order_item = models.ForeignKey(OrderItem,
                                   related_name='item_option_finishes',
                                   on_delete=models.CASCADE)
    option_value = models.ForeignKey(OptionValue, on_delete=models.CASCADE)
    finish_option = models.ForeignKey(FinishOption, on_delete=models.CASCADE)

    class Meta:
        # Define the plural correctly
        verbose_name_plural = 'Option Finishes'

    def __str__(self):
        return (f"{self.order_item} - {self.option_value.value} - "
                f"{self.finish_option.name}")
