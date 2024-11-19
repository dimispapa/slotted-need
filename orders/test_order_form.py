from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker
from products.models import Product, OptionValue


class TestCreateOrderView(TestCase):
    """
    Test case for the Create Order view
    """

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password='testpass')

        # Create test products and options
        self.product = baker.make(Product)
        self.option_value = baker.make(OptionValue, option__product=self.product)

        # Define the URL for creating an order
        self.create_order_url = reverse('create_order')
