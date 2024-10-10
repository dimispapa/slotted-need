from django.test import TestCase, Client
from django.urls import reverse
from orders.factories import UserFactory


class TestHomeView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password='testpass')

    def test_home_renders_correctly(self):
        """Test for the home view rendering correctly"""
        response = self.client.get(reverse('home'))

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
