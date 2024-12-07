from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from model_bakery import baker
from orders.models import OrderItem, Order
from products.models import Product
from rest_framework import status


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
        self.product2 = baker.make(Product)
        self.order = baker.make(Order)
        self.order2 = baker.make(Order)
        self.order_item_high_priority = baker.make(
            OrderItem, order=self.order, product=self.product,
            priority_level=3, completed=False
        )
        self.order_item_critical = baker.make(
            OrderItem, order=self.order, product=self.product, order__paid=2,
            item_status=1, completed=False
        )
        self.order_item = baker.make(
            OrderItem,
            order=self.order2,
            product=self.product2,
        )

        self.page_url = reverse('order_item_tracker')
        # For /api/order-items/
        self.list_api_url = reverse('orderitem-list')
        # For /api/order-items/<id>/
        self.detail_api_url = reverse('orderitem-detail',
                                      args=[self.order_item.id])

    def test_order_item_view_renders_correctly(self):
        """
        Test for rendering the order iten view with the correct template
        """
        response = self.client.get(self.page_url)
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

        # check critical items count
        critical_items_count = OrderItem.objects.filter(
            (
                Q(order__paid=2, item_status=1) |
                Q(order__paid=1, item_status=4) |
                Q(priority_level=3)
            ) & Q(completed=False)
        ).count()
        self.assertEqual(critical_items_count,
                         response.context['critical_items_count'],
                         msg='Critical items count discrepancy')

    def test_list_order_items(self):
        """
        Test the list endpoint for order items.
        """
        response = self.client.get(self.list_api_url)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Order item API endpoint failed")
        data = response.json()
        self.assertEqual(data['count'], 3,
                         "Incorrect number of order items returned")

    def test_retrieve_order_item(self):
        """
        Test the retrieve endpoint for a specific order item.
        """
        response = self.client.get(self.detail_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], self.order_item.id)
        self.assertEqual(data['product']['id'], self.product2.id)
