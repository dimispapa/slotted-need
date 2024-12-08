from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker
from orders.models import Order
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
                                archived=True)
        self.order2 = baker.make(Order,
                                 archived=False)

        self.page_url = reverse('order_archive')
        # For /api/orders/
        self.list_api_url = reverse('order-list')
        # Archive/Unarchive actions
        self.archive_url = reverse('order-archive',
                                   kwargs={'pk': self.order2.id})
        self.unarchive_url = reverse('order-unarchive',
                                     kwargs={'pk': self.order.id})

    def test_order_archive_view_renders_correctly(self):
        """
        Test for rendering the order archive view with the correct template
        """
        response = self.client.get(self.page_url)
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200, msg='Response NOT OK')
        # Check that the correct template was used
        self.assertTemplateUsed(response, 'orders/archive.html')
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

    def test_list_archived_orders(self):
        """
        Test the list endpoint for order archive.
        """
        response = self.client.get(self.list_api_url, {'archived': True})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Order item API endpoint failed")
        data = response.json()
        archive_count = Order.objects.filter(archived=True).count()
        self.assertEqual(data['count'], archive_count,
                         "Incorrect number of archived orders returned")

    def test_archive_order(self):
        """
        Test the archive action for an order.
        """
        # Make a POST request to archive the order
        response = self.client.post(self.archive_url)

        # Refresh the order from the database
        self.order2.refresh_from_db()

        # Check the response status code
        self.assertEqual(response.status_code, 200,
                         "Response status code is not 200.")
        # Check the response message
        self.assertEqual(response.data['message'],
                         f'Order {self.order2.id} archived.',
                         "Incorrect success message.")
        # Verify that the order is archived
        self.assertTrue(self.order2.archived, "Order was not archived.")

    def test_unarchive_order(self):
        """
        Test the unarchive action for an order.
        """
        # Archive the order first
        self.order.archived = True
        self.order.save()

        # Make a POST request to unarchive the order
        response = self.client.post(self.unarchive_url)

        # Refresh the order from the database
        self.order.refresh_from_db()

        # Check the response status code
        self.assertEqual(response.status_code, 200,
                         "Response status code is not 200.")
        # Check the response message
        self.assertEqual(response.data['message'],
                         f'Order {self.order.id} un-archived.',
                         "Incorrect success message.")
        # Verify that the order is no longer archived
        self.assertFalse(self.order.archived, "Order was not un-archived.")

    def test_invalid_archive_request(self):
        """
        Test that attempting to archive a non-existent order returns a 404.
        """
        invalid_url = reverse('order-archive',
                              kwargs={'pk': 999})  # Non-existent ID
        response = self.client.post(invalid_url)

        # Check that the response returns a 404 status
        self.assertEqual(response.status_code, 404,
                         "Response status code is not 404.")

    def test_invalid_unarchive_request(self):
        """
        Test that attempting to unarchive a non-existent order returns a 404.
        """
        invalid_url = reverse('order-unarchive',
                              kwargs={'pk': 999})  # Non-existent ID
        response = self.client.post(invalid_url)

        # Check that the response returns a 404 status
        self.assertEqual(response.status_code, 404,
                         "Response status code is not 404.")
