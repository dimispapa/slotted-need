from django.db import models
from products.models import Product, OptionValue, FinishOption


# Create your models here.
class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items',
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    option_value = models.ManyToManyField(OptionValue,
                                          related_name='order_items')
    finishes = models.ManyToManyField(FinishOption, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
