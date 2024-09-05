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
    discount = models.DecimalField(max_digits=7, decimal_places=2,
                                   validators=[MinValueValidator(0.00)],
                                   default=0.00)
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

    def __str__(self):
        return f"Order #{self.id} by {self.client.client_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items',
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    option_values = models.ManyToManyField(OptionValue,
                                           related_name='order_items')
    finishes = models.ManyToManyField(FinishOption, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
