from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce
from orders.models import Client as ClientModel, OrderItem
from .utils import generate_unique_rgba_colors
from products.models import Product
from model_bakery import baker


class TestHomeView(TestCase):
    """
    Test case for testing the Home view
    """

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

    def test_home_renders_correctly(self):
        """
        Test for the home view rendering correctly for an admin
        """
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

    def test_non_admin_cannot_access(self):
        """
        Test that a non-admin user cannot access
        """
        # Create a client with non-admin user
        self.user = baker.make(User, is_staff=False, is_superuser=False)
        self.user.set_password('testpass')
        self.user.save()
        self.client.login(username=self.user.username, password='testpass')

        response = self.client.get(reverse('home'))

        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestProductRevenueDataAPI(TestCase):
    """
    Test case for testing the ProductRevenueDataAPIView
    """

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

        # Create test data
        self.customer = baker.make('orders.Client')
        self.order = baker.make('orders.Order',
                                client=self.customer)
        self.order_item = baker.make('orders.OrderItem',
                                     order=self.order,
                                     )
        self.order_item2 = baker.make('orders.OrderItem',
                                      order=self.order,
                                      )

    def test_product_revenue_data_admin(self):
        """
        Test if the product revenue data response from the API
        matches the product and order item instances of the order
        """
        # make an API request
        response = self.client.get(reverse('product_revenue_data'))
        # check for 200 status code
        self.assertEqual(response.status_code, 200)
        # parse json data
        data = response.json()

        # Assert if the correct labels and values are in the response
        # that chartjs charts use to render data
        expected_labels = sorted([item.product.name
                                  for item in self.order.items.all()])
        expected_values = sorted([float(item.item_value)
                                  for item in self.order.items.all()])
        self.assertListEqual(expected_labels, sorted(data['labels']))
        self.assertListEqual(expected_values, sorted(data['values']))

    def test_product_revenue_data_non_admin(self):
        """
        Test a request from a non-admin user to ensure
        that it gets rejected
        """
        # Create a client with non-admin user
        self.user = baker.make(User, is_staff=False, is_superuser=False)
        self.user.set_password('testpass')
        self.user.save()
        self.client.login(username=self.user.username, password='testpass')

        # make an API request
        response = self.client.get(reverse('product_revenue_data'))
        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestDebtorBalancesAPI(TestCase):
    """
    Test case for testing the DebtorBalancesAPIView
    """

    def setUp(self):
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

        # Create test data
        self.customers = baker.make('orders.Client',
                                    _quantity=3,
                                    _bulk_create=True)
        self.order_unpaid = baker.make('orders.Order',
                                       client=self.customers[0],
                                       # set as unpaid
                                       paid=1)
        self.order_paid = baker.make('orders.Order',
                                     client=self.customers[1],
                                     # set as paid
                                     paid=2)
        self.order_item = baker.make('orders.OrderItem',
                                     order=self.order_unpaid,
                                     )
        self.order_item2 = baker.make('orders.OrderItem',
                                      order=self.order_unpaid,
                                      )
        self.order_item3 = baker.make('orders.OrderItem',
                                      order=self.order_paid,
                                      )

    def test_debtor_balances_data_admin(self):
        """
        Test if the debtor balances data response from the API
        matches the order object instances
        """
        # make an API request
        response = self.client.get(reverse('debtors_balances_data'))
        # check for 200 status code
        self.assertEqual(response.status_code, 200)
        # parse json data
        data = response.json()

        # create the debtors objects based on the same API criteria
        debtors = ClientModel.objects.filter(orders__paid=1).annotate(
            balance_owed=Coalesce(
                Sum('orders__order_value'), 0,
                output_field=DecimalField()
            )
        ).order_by('-balance_owed')

        # prepare expected data
        expected_labels = [debtor.client_name for debtor in debtors]
        expected_values = [float(debtor.balance_owed) for debtor in debtors]

        # Assert if the correct labels and values are in the response
        # that chartjs charts use to render data
        self.assertListEqual(expected_labels, sorted(data['labels']))
        self.assertListEqual(expected_values, sorted(data['values']))
        self.assertEqual(sum(expected_values), data['total'])

    def test_product_revenue_data_non_admin(self):
        """
        Test a request from a non-admin user to ensure
        that it gets rejected
        """
        # Create a client with non-admin user
        self.user = baker.make(User, is_staff=False, is_superuser=False)
        self.user.set_password('testpass')
        self.user.save()
        self.client.login(username=self.user.username, password='testpass')

        # make an API request
        response = self.client.get(reverse('debtors_balances_data'))
        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')
