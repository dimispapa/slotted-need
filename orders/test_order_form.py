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
        self.option_value = baker.make(OptionValue,
                                       option__product=self.product)

        # Define the URL for creating an order
        self.create_order_url = reverse('create_order')

    def test_create_order_view_renders_correctly(self):
        """
        Test for rendering the create order view with the correct template
        """
        response = self.client.get(self.create_order_url)
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200, msg='Response NOT OK')
        # Check that the correct template was used
        self.assertTemplateUsed(response, 'orders/create_order.html')
        # Check if form and formset are in the response context
        self.assertIn('order_form', response.context,
                      msg='Order form missing in context')
        self.assertIn('order_item_formset', response.context,
                      msg='Order item formset missing in context')
