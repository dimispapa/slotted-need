from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce
import numbers
from orders.models import Client as ClientModel, OrderItem
from .utils import generate_unique_rgba_colors
from products.models import Product
from model_bakery import baker


class TestHomeView(TestCase):
    """
    Test case for testing the Home view
    """

    def setUp(self):
        self.url_name = 'home'
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
        response = self.client.get(reverse(self.url_name))

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
        self.user_nonadmin = baker.make(User,
                                        is_staff=False,
                                        is_superuser=False)
        self.user_nonadmin.set_password('testpass')
        self.user_nonadmin.save()
        self.client.login(username=self.user_nonadmin.username,
                          password='testpass')

        response = self.client.get(reverse(self.url_name))

        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestProductRevenueDataAPI(TestCase):
    """
    Test case for testing the ProductRevenueDataAPIView
    """

    def setUp(self):
        self.api_name = 'product_revenue_data'
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

    def test_product_revenue_data(self):
        """
        Test if the product revenue data response from the API
        matches the product and order item instances of the order
        """
        # make an API request
        response = self.client.get(reverse(self.api_name))
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
        self.user_nonadmin = baker.make(User,
                                        is_staff=False,
                                        is_superuser=False)
        self.user_nonadmin.set_password('testpass')
        self.user_nonadmin.save()
        self.client.login(username=self.user_nonadmin.username,
                          password='testpass')

        # make an API request
        response = self.client.get(reverse(self.api_name))
        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestDebtorBalancesAPI(TestCase):
    """
    Test case for testing the DebtorBalancesAPIView
    """

    def setUp(self):
        self.api_name = 'debtors_balances_data'
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

    def test_debtor_balances_data(self):
        """
        Test if the debtor balances data response from the API
        matches the order object instances
        """
        # make an API request
        response = self.client.get(reverse(self.api_name))
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
        self.user_nonadmin = baker.make(User,
                                        is_staff=False,
                                        is_superuser=False)
        self.user_nonadmin.set_password('testpass')
        self.user_nonadmin.save()
        self.client.login(username=self.user_nonadmin.username,
                          password='testpass')

        # make an API request
        response = self.client.get(reverse(self.api_name))
        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestItemStatusProductAPI(TestCase):
    """
    Test case for testing the ItemStatusProductAPIView
    """

    def setUp(self):
        self.api_name = 'item_status_product_data'
        # Create a superuser / admin
        self.user = baker.make(User, is_staff=True, is_superuser=True)
        self.user.set_password('testpass')
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

        # Create test data
        self.order_items = baker.make('orders.OrderItem',
                                      _quantity=10,
                                      _bulk_create=True
                                      )

    def test_item_status_product_data(self):
        """
        Test if the item status product data response from the API
        matches the order item object instances
        """
        # make an API request
        response = self.client.get(reverse(self.api_name))
        # check for 200 status code
        self.assertEqual(response.status_code, 200)
        # parse json data
        data = response.json()

        # create the debtors objects based on the same API criteria
        # Fetch OrderItems filtering out made, delivered and archived orders
        order_items = OrderItem.objects.filter(
            completed=False).select_related(
            'product').prefetch_related(
            'option_values', 'item_component_finishes').order_by(
            'id')

        # Fetch products list
        products = Product.objects.all()

        # Aggregate counts by item_status
        status_counts = list(
            order_items.values(
                'item_status', 'product__name').order_by(
                    'item_status').annotate(
                        count=Count('id')))

        # Pull the mapping with status codes to human-readable labels
        status_mapping = OrderItem.STATUS_CHOICES
        # Initialize empty datasets list
        expected_datasets = []
        # Get unique rgba colors list using util function
        colors = generate_unique_rgba_colors(len(products), border_color=True)

        # Ensure all statuses are represented, even with zero counts
        for idx, product in enumerate(products):
            count_data = []
            # Ensure all statuses are represented, even with zero counts
            for status_code in status_mapping.keys():
                # Find if this status exists in the aggregated data
                matching = next((item for item in status_counts
                                if item['product__name'] == product.name
                                and item['item_status'] == status_code),
                                None)
                count_data.append(matching['count'] if matching else 0)

            bg_color, bd_color = colors[idx]

            expected_dataset = {
                'label': product.name,
                'data': count_data,
                'backgroundColor': bg_color,
                'borderColor': bd_color,
                'borderWidth': 1
            }
            expected_datasets.append(expected_dataset)

        # prepare expected data
        expected_labels = sorted([label for label in status_mapping.values()])
        sorted_expected_datasets = sorted(expected_datasets,
                                          key=lambda x: x['label'])
        # prepare regex pattern for the rgba colour string
        START = r'^rgba\('
        END = r'\)$'
        # regex for integers between 0 and 255:
        RGB = r'(0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])'
        # regex pattern that matches floats between 0 and 1 inclusive,
        # allowing for decimal fractions.
        ALPHA = r'(0(?:\.\d+)?|1(?:\.0+)?)'
        # putting it all together for full regex pattern
        RGBA_REGEX = rf"{START}({RGB}),\s*({RGB}),\s*({RGB}),\s*({ALPHA}){END}"

        # sort response labels and dataset dicts
        sorted_data_labels = sorted(data['labels'])
        sorted_response_datasets = sorted(data['datasets'],
                                          key=lambda x: x['label'])

        # Assert if the correct labels and values are in the response
        # that chartjs charts use to render data
        # assert x-axis labels
        self.assertListEqual(expected_labels, sorted_data_labels)
        # loop through dataset dicts and assert values
        for idx, dataset in enumerate(sorted_response_datasets):
            # assert dataset label
            self.assertEqual(sorted_expected_datasets[idx]['label'],
                             dataset['label'])
            # assert dataset values
            self.assertListEqual(sorted(sorted_expected_datasets[idx]['data']),
                                 sorted(dataset['data']))
            # assert background color and border color rgba strings
            self.assertRegex(sorted_expected_datasets[idx]['backgroundColor'],
                             RGBA_REGEX)
            self.assertRegex(sorted_expected_datasets[idx]['borderColor'],
                             RGBA_REGEX)
            # Check if border width is a number
            self.assertIsInstance(sorted_expected_datasets[idx]['borderWidth'],
                                  numbers.Number)

    def test_item_status_product_data_non_admin(self):
        """
        Test a request from a non-admin user to ensure
        that it gets rejected
        """
        # Create a client with non-admin user
        self.user_nonadmin = baker.make(User,
                                        is_staff=False,
                                        is_superuser=False)
        self.user_nonadmin.set_password('testpass')
        self.user_nonadmin.save()
        self.client.login(username=self.user_nonadmin.username,
                          password='testpass')

        # make an API request
        response = self.client.get(reverse(self.api_name))
        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')


class TestItemStatusConfigAPI(TestCase):
    """
    Test case for testing the ItemStatusConfigAPIView
    """

    def setUp(self):
        # Create a superuser / admin
        self.user_nonadmin = baker.make(User, is_staff=True, is_superuser=True)
        self.user_nonadmin.set_password('testpass')
        self.user_nonadmin.save()
        self.client = Client()
        self.client.login(username=self.user_nonadmin.username,
                          password='testpass')

        # Create test data
        self.order_items = baker.make('orders.OrderItem',
                                      _quantity=10,
                                      _bulk_create=True
                                      )
