from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker
from orders.models import OrderItem, Order
from products.models import Product
from rest_framework import status


class TestOrderViewSet(TestCase):
    """
    Test case for the OrderViewSet
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
        self.order = baker.make(Order,
                                paid=1)
        self.order2 = baker.make(Order,
                                 paid=2)
        self.order_item1 = baker.make(
            OrderItem, order=self.order,
            product=self.product
        )
        self.order_item2 = baker.make(
            OrderItem,
            order=self.order2,
            product=self.product2,
            item_status=1,
            priority_level=1
        )

        self.page_url = reverse('order_tracker')
        # For /api/orders/
        self.list_api_url = reverse('order-list')
        # For /api/orders/<id>/
        self.detail_api_url = reverse('order-detail',
                                      args=[self.order.id])

    def test_order_view_renders_correctly(self):
        """
        Test for rendering the order view with the correct template
        """
        response = self.client.get(self.page_url)
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200, msg='Response NOT OK')
        # Check that the correct template was used
        self.assertTemplateUsed(response, 'orders/orders.html')
        # Check if context variables are passed to template
        self.assertIn('order_status_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('item_status_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('priority_level_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('paid_status_choices', response.context,
                      msg='Context variable missing')
        self.assertIn('order_status_choices_json', response.context,
                      msg='Context variable missing')
        self.assertIn('item_status_choices_json', response.context,
                      msg='Context variable missing')
        self.assertIn('priority_level_choices_json', response.context,
                      msg='Context variable missing')
        self.assertIn('paid_status_choices_json', response.context,
                      msg='Context variable missing')

    def test_list_orders(self):
        """
        Test the list endpoint for orders.
        """
        response = self.client.get(self.list_api_url)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Order item API endpoint failed")
        data = response.json()
        self.assertEqual(data['count'], 2,
                         "Incorrect number of orders returned")

    def test_retrieve_order(self):
        """
        Test the retrieve endpoint for a specific order.
        """
        response = self.client.get(self.detail_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], self.order.id)
        self.assertEqual(data['paid'], 1)

    def test_update_order(self):
        """
        Test updating an existing order.
        """
        data = {
            'paid': 2
        }
        response = self.client.patch(self.detail_api_url, data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid, 2)

    def test_delete_order(self):
        """
        Test deleting an order.
        """
        response = self.client.delete(self.detail_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(OrderItem.objects.filter(
            id=self.order.id).exists())
