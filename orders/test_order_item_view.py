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
        self.order_items_url = reverse('order_item_tracker')

    def test_order_item_view_renders_correctly(self):
        """
        Test for rendering the order iten view with the correct template
        """
        response = self.client.get(self.order_items_url)
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200, msg='Response NOT OK')
        # Check that the correct template was used
        self.assertTemplateUsed(response, 'orders/order_items.html')
        # Check if context variables are passed to template
        self.assertIn('item_status_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('priority_level_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('paid_status_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('item_status_choices_json', response.context,
                      msg='Context variable missing')
        self.assertIn('priority_level_choices_json', response.context,
                      msg='Context variable missing')
        self.assertIn('paid_status_choices_json', response.context,
                      msg='Context variable missing')
