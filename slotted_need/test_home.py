from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker


class TestHomeView(TestCase):

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

    def test_home_renders_correctly(self):
        """Test for the home view rendering correctly"""
        response = self.client.get(reverse('home'))

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200,
                         msg='Response NOT OK')

        # Check that the correct template was used
        self.assertTemplateUsed(response, 'home.html')

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

        # Check if canvas and table elements exist
        self.assertContains(response, b'canvas')
        self.assertContains(response, b'orderitem-home-table')


class ProductRevenueAPITest(TestCase):

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

        # Create test data
        self.product = baker.make('products.Product')
        self.product2 = baker.make('products.Product')
        self.customer = baker.make('orders.Client')

        self.order = baker.make('orders.Order',
                                client=self.customer)
        self.order_item = baker.make('orders.OrderItem',
                                     order=self.order,
                                     product=self.product)
        self.order_item2 = baker.make('orders.OrderItem',
                                      order=self.order,
                                      product=self.product2)

    def test_product_revenue_data(self):
        """
        Test if the product revenue data response from the API
        matches the product and order item instances of the order
        """
        response = self.client.get(reverse('product_revenue_data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        expected_labels = [self.product.name, self.product2.name]
        expected_values = [float(self.order_item.item_value),
                           float(self.order_item2.item_value)]

        self.assertEqual(data['labels'], expected_labels)
        self.assertEqual(data['values'], expected_values)
