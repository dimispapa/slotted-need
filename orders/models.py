from decimal import Decimal
from django.db import models
from django.db.models import Case, When, Value, BooleanField
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
from products.models import Product, OptionValue, FinishOption, Component


class Client(models.Model):
    client_name = models.CharField(max_length=100)
    client_phone = PhoneNumberField(blank=True)
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
    # create a PROGRESS status mapping to use as choices for order_status
    STATUS_CHOICES = {1: 'Not Started',
                      2: 'In Progress',
                      3: 'Made',
                      4: 'Delivered'}
    order_status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        editable=False,  # Prevents editing in forms and admin
    )
    # create a PAID status mapping to use as choices for order_status
    PAID_CHOICES = {1: 'Not Paid',
                    2: 'Fully Paid'}
    paid = models.IntegerField(
        choices=PAID_CHOICES,
        default=1
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)

    def calculate_totals(self):
        """Calculate the total discount and order value based
        on order items."""
        # Ensure there are items before trying to calculate totals
        items = self.items.all()
        if items.exists():  # Only calculate if there are items
            self.discount = sum(item.discount for item in items
                                if item.discount)
            self.order_value = sum(item.item_value for item in items
                                   if item.item_value)

    def update_order_status(self):
        """Automatically derive the order status based on conditions
        set on the child items' item_status fields."""
        # Get all item statuses
        item_statuses = self.items.values_list('item_status', flat=True)

        # If no items exist set to not started
        if not item_statuses:
            new_status = 1
        # Check for 'Not Started'
        elif all(status == 1 for status in item_statuses):
            new_status = 1
        # Check for 'Delivered'
        elif all(status == 4 for status in item_statuses):
            new_status = 4
        # Check for 'Made'
        elif all(status == 3 for status in item_statuses):
            new_status = 3
        # Check for 'In Progress'
        elif any(status == 2 for status in item_statuses):
            new_status = 2
        else:
            # Default to 'In Progress' if any other combination
            new_status = 2

        # Update the order_status if it has changed
        if self.order_status != new_status:
            self.order_status = new_status
            # Save the order without triggering update_order_status again
            super(Order, self).save(update_fields=['order_status'])

    class Meta:
        ordering = ["-created_on"]

    def save(self, *args, **kwargs):
        # Only execute custom methods after the object has been saved
        # and has a primary key
        if self.pk:
            # calculate order totals
            self.calculate_totals()
            # Check if 'paid' status has changed
            old_paid = Order.objects.get(pk=self.pk).paid
        else:
            old_paid = None

        # save Order object
        super().save(*args, **kwargs)

        # If 'paid' status has changed, update related OrderItems
        # by evaluating if it meets the conditions to update 'completed' field
        if old_paid != self.paid:
            self.items.all().update(
                completed=Case(
                    When(item_status=4, then=Value(self.paid == 2)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )

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
    option_values = models.ManyToManyField(OptionValue,
                                           related_name='order_items',
                                           blank=True
                                           )
    product_finish = models.ForeignKey(FinishOption, on_delete=models.SET_NULL,
                                       blank=True, null=True,
                                       related_name='order_items'
                                       )
    # create a status mapping to use as choices for order_status
    STATUS_CHOICES = {1: 'Not Started',
                      2: 'In Progress',
                      3: 'Made',
                      4: 'Delivered'}
    item_status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1
    )
    # create a priority level field and use a mapping for choices
    PRIORITY_CHOICES = {1: 'Low',
                        2: 'Medium',
                        3: 'High'}
    priority_level = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1
    )
    completed = models.BooleanField(default=False)

    def calculate_item_value(self):
        # Ensure base_price and discount are converted from None
        base_price = self.base_price or Decimal('0.00')
        discount = self.discount or Decimal('0.00')
        # Automatically calculate item_value before saving
        self.item_value = base_price - discount

    def update_completed(self):
        """Automatically update the completed and priority level fields
        based on conditions set on the item_status and its parent's paid
        fields."""
        # Get the item status and order's paid status
        item_status = self.item_status
        paid = self.order.paid

        # Delivered and Fully Paid set to completed
        if item_status == 4 and paid == 2:
            completed = True
        else:
            completed = False

        # Update completed field if it has changed
        if self.completed != completed:
            self.completed = completed

    def save(self, *args, **kwargs):
        # call custom methods before saving
        self.calculate_item_value()
        self.update_completed()
        self.order.update_order_status()

        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Order Item #{self.id} - {self.product.name}: "
                f"€{self.item_value}")

    def delete(self, *args, **kwargs):
        order = self.order  # Keep a reference to the order
        super().delete(*args, **kwargs)
        # Update the order's status after deleting the item
        order.update_order_status()

    # define a property method that generates unique configuration string
    @property
    def unique_configuration(self):
        """
        Generates a unique concatenated string representing the combination of
        Product name, Option Values, Product Finish, and Component Finishes.
        """
        product_name = self.product.name
        product_finish = self.product_finish

        # Retrieve and sort option values
        option_values = sorted(
            self.option_values.values_list('value', flat=True)
        )
        option_values_str = (', '.join(option_values)
                             if option_values else None)

        # Retrieve and sort component finishes
        finishes = sorted(
            self.item_component_finishes.values_list('finish_option__name',
                                                     flat=True)
        )
        # add product finish to start of list if not None
        if product_finish:
            finishes.insert(0, product_finish)
        # create finishes string
        finishes_str = ', '.join(finishes) if finishes else None

        # Concatenate all parts into a single string
        unique_config = (
            f"{product_name}" +
            (f" | {option_values_str}"
             if option_values_str else "") +
            (f" | {finishes_str}"
             if finishes_str else "")
        )
        return unique_config


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
        return (f"{self.component.name} - "
                f"{self.finish_option.name}")
