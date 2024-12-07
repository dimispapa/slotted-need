from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker
from orders.models import OrderItem, Order
from products.models import Product


class TestOrderItemViewSet(TestCase):
    """
    Test case for the OrderItemViewSet
    """

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password='testpass')

        # Create test data
        self.product = baker.make(Product)
        self.order = baker.make(Order)
        self.order_item_high_priority = baker.make(
            OrderItem, order=self.order, product=self.product,
            priority_level=3, completed=False
        )
        self.order_item_critical = baker.make(
            OrderItem, order=self.order, product=self.product, order__paid=2,
            item_status=1, completed=False
        )
        self.api_url = reverse('order_item_tracker')
