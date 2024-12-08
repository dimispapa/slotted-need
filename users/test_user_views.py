from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from model_bakery import baker
from unittest.mock import patch


class TestUserViews(TestCase):
    """
    Test suite for user views.
    """

    def setUp(self):
        # Create a superuser for accessing admin-only views
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client = Client()
        self.client.login(username='admin', password='adminpass')

        # Create the 'Admin Group' used in views/forms
        self.admin_group = baker.make(Group, name='Admin Group')

        # Create a regular user
        self.regular_user = baker.make(User)

        # URLs for views
        self.user_list_url = reverse('user_list')
        self.user_create_url = reverse('user_add')
        self.user_update_url = reverse('user_edit',
                                       args=[self.regular_user.id])
        self.user_delete_url = reverse('user_delete',
                                       args=[self.regular_user.id])

    def test_user_list_view_accessible(self):
        """
        Test that the user list view is accessible to logged-in users.
        """
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 200,
                         msg='User list view not accessible.')
        self.assertTemplateUsed(response, 'users/user_list.html')
        self.assertIn('users', response.context)

    def test_user_create_view_accessible(self):
        """
        Test that the user create view is accessible to admin users.
        """
        response = self.client.get(self.user_create_url)
        self.assertEqual(response.status_code, 200,
                         msg='User create view not accessible.')
        self.assertTemplateUsed(response, 'users/user_form.html')
        self.assertIn('form', response.context)

    def test_user_update_view_accessible(self):
        """
        Test that the user update view is accessible to admin users.
        """
        response = self.client.get(self.user_update_url)
        self.assertEqual(response.status_code, 200,
                         msg='User update view not accessible.')
        self.assertTemplateUsed(response, 'users/user_form.html')
        self.assertIn('form', response.context)

    def test_user_delete_view_accessible(self):
        """
        Test that the user delete view is accessible to admin users.
        """
        response = self.client.get(self.user_delete_url)
        self.assertEqual(response.status_code, 200,
                         msg='User delete view not accessible.')
        self.assertTemplateUsed(response, 'users/user_confirm_delete.html')

    def test_resend_invite_view(self):
        """
        Test that the resend invite functionality works correctly.
        """
        user = baker.make(User, is_active=False)
        url = reverse('resend_invite', args=[user.id])

        with patch('users.views.send_invitation_email') as mock_send_email:
            mock_send_email.return_value = (True, None)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 302,
                             msg='Resend invite did not redirect.')
            self.assertTrue(mock_send_email.called,
                            msg='Invitation email was not sent.')
            mock_send_email.assert_called_with(user, response.wsgi_request)

    def test_user_permissions(self):
        """
        Test that non-admin users cannot access admin-only views.
        """
        self.client.logout()
        self.client.login(username='user', password='userpass')

        # Attempt to access user create view
        response = self.client.get(self.user_create_url)
        self.assertNotEqual(response.status_code, 200,
                            msg='Non-admin user should not access '
                            'user create view.')

        # Attempt to access user delete view
        response = self.client.get(self.user_delete_url)
        self.assertNotEqual(response.status_code, 200,
                            msg='Non-admin user should not access '
                            'user delete view.')

    def test_user_delete_view_functionality(self):
        """
        Test that the delete functionality works correctly.
        """
        response = self.client.post(self.user_delete_url)
        self.assertEqual(response.status_code, 302,
                         msg='User delete view did not redirect.')
        self.assertFalse(User.objects.filter(
            id=self.regular_user.id).exists(), msg='User was not deleted.')
