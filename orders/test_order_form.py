from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from model_bakery import baker
from products.models import Product, OptionValue
from orders.models import Order, Client as ClientModel
from orders.forms import OrderForm, OrderItemFormSet
from orders.views import get_update_create_client


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
        self.product2 = baker.make(Product)
        self.option_value = baker.make(OptionValue,
                                       option__product=self.product)
        self.option_value2 = baker.make(OptionValue,
                                        option__product=self.product2)

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
        self.assertIsInstance(response.context['order_form'],
                              OrderForm)
        self.assertIsInstance(response.context['order_item_formset'],
                              OrderItemFormSet)

    def test_create_order_with_valid_data(self):
        """
        Test create order form submission with valid data
        """
        data = {
            'client_name': 'Test Client',
            'client_phone': '+35799999999',
            'client_email': 'testclient@example.com',
            'order_value': '700.00',
            'deposit': '20.00',
            'items-TOTAL_FORMS': '2',
            'items-INITIAL_FORMS': '0',
            'items-0-product': self.product.id,
            'items-0-quantity': '1',
            'items-0-base_price': '220.00',
            'items-0-discount': '0.00',
            'items-0-item_value': '220.00',
            'items-0-option_1': self.option_value.id,
            'items-1-product': self.product2.id,
            'items-1-quantity': '3',
            'items-1-base_price': '180.00',
            'items-1-discount': '20.00',
            'items-1-item_value': '160.00',
            'items-1-option_2': self.option_value2.id,
        }
        # Check if the check client API is working as expected
        # before posting form data
        check_client_response = self.client.post(reverse('check_client'), data)
        # post the form data
        response = self.client.post(self.create_order_url, data)
        # pass the post request to the form and formset objects
        order_form = OrderForm(data=data)
        order_item_formset = OrderItemFormSet(data, prefix='items')

        # check if the form and forsmet have no errors
        self.assertTrue(order_form.is_valid())
        self.assertTrue(order_item_formset.is_valid())
        # Check if the form submission was successful
        self.assertEqual(response.status_code, 302, msg='Redirect NOT OK')

        # Check client API tests
        check_client_response_data = check_client_response.json()
        # Verify that the partial match and exact match are false
        self.assertFalse(check_client_response_data['exact_match'],
                         msg='Incorrect exact match')
        self.assertFalse(check_client_response_data['partial_match'],
                         msg='Incorrect partial match')
        # Check if the new test client (customer) was created successfully
        self.assertTrue(Order.objects.filter(client__client_name='Test Client'
                                             ).exists(),
                        msg='Client was not created')

    def test_create_order_with_invalid_data(self):
        """
        Test create order form submission with invalid data
        """
        data = {
            'client_name': '',  # Missing client name
            'client_phone': '+35799999999',
            'client_email': 'invalidemail',  # Invalid email format
            'order_value': '-100.00',
            'deposit': '20.00',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-0-product': self.product.id,
            'items-0-quantity': '-1',  # Negative quantity
            'items-0-base_price': '-100.00',  # Negative base price
            'items-0-discount': '0.00',
            'items-0-item_value': '-100.00',  # Negative item value
        }

        response = self.client.post(self.create_order_url, data)
        # Check that the response is 200,
        # meaning the form re-renders with errors
        self.assertEqual(response.status_code, 200,
                         msg='Invalid form did not re-render correctly')
        # pass the post request to the form and formset objects
        order_form = OrderForm(data=data)
        order_item_formset = OrderItemFormSet(data, prefix='items')
        # check if the form has all expected errors
        self.assertFalse(order_form.is_valid())
        self.assertIn('client_name', order_form.errors)
        self.assertIn('client_email', order_form.errors)
        # Check errors in the OrderItemFormSet
        self.assertFalse(order_item_formset.is_valid(),
                         msg='Order item formset should be invalid')
        for form in order_item_formset:
            self.assertIn('base_price', form.errors)
            self.assertIn('item_value', form.errors)
            self.assertIn('quantity', form.errors)

    def test_client_exact_match_handling(self):
        """
        Test client conflict handling with exact match
        """
        # Create an existing client to trigger conflict
        existing_client = baker.make(ClientModel,
                                     client_name='Existing Client',
                                     client_phone='+35799999999',
                                     client_email='existingclient@example.com')

        # Use the same details for a new order to trigger the conflict modal
        data = {
            'client_name': 'Existing Client',
            'client_phone': '+35799999999',
            'client_email': 'existingclient@example.com',
            'order_value': '100.00',
            'deposit': '20.00',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-0-product': self.product.id,
            'items-0-quantity': '1',
            'items-0-base_price': '100.00',
            'items-0-discount': '0.00',
            'items-0-item_value': '100.00',
        }

        response = self.client.post(reverse('check_client'), data)
        response_data = response.json()
        # Verify that the exact match is returned
        self.assertIn('exact_match', response_data,
                      msg='Exact match not detected')
        self.assertEqual(response_data['exact_match']['id'],
                         existing_client.id,
                         msg='Incorrect client match')

    def test_client_partial_match_handling(self):
        """
        Test client conflict handling with partial match
        i.e. matching name and phone, but non-matching email
        and test handling of updating client data
        """
        # Create an existing client to trigger conflict
        existing_client = baker.make(ClientModel,
                                     client_name='Existing Client',
                                     client_phone='+35799999999',
                                     client_email='existclient@example.com')

        # Use the same details for a new order to trigger the conflict modal
        data = {
            'client_name': 'Existing Client',  # matching
            'client_phone': '+35799999999',  # matching
            'client_email': 'existingcustomer@example.com',  # non-matching
            'order_value': '100.00',
            'deposit': '20.00',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-0-product': self.product.id,
            'items-0-quantity': '1',
            'items-0-base_price': '100.00',
            'items-0-discount': '0.00',
            'items-0-item_value': '100.00',
        }

        response = self.client.post(reverse('check_client'), data)
        response_data = response.json()
        # Verify that the partial match is returned
        self.assertIn('partial_match', response_data,
                      msg='Partial match not detected')
        self.assertEqual(response_data['partial_match']['id'],
                         existing_client.id,
                         msg='Incorrect client match')

        # Update the existing client
        client = get_update_create_client(action='update_client',
                                          client_id=existing_client.id,
                                          cleaned_data=data)
        # Verify that the client details were updated
        self.assertEqual(client.client_email, 'existingcustomer@example.com',
                         msg='Client email was not updated correctly')

    def test_non_user_cannot_access(self):
        """
        Test a request without logged-in user to ensure
        that it gets rejected
        """
        # Create a client with no logged in user
        self.client_loggedout = Client()

        response = self.client_loggedout.get(self.create_order_url)

        # check for non 200 status code
        self.assertNotEqual(response.status_code, 200,
                            msg='Anauthorised access allowed')
