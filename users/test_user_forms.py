from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from model_bakery import baker
from users.forms import CustomUserCreationForm, CustomUserChangeForm


class TestUserFormsAndViews(TestCase):
    """
    Test cases for user forms and views.
    """

    def setUp(self):
        # Create a superuser/admin for testing views
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client = Client()
        self.client.login(username='admin', password='adminpass')

        # Create the 'Admin Group' used in the forms
        self.admin_group = Group.objects.create(name='Admin Group')

        # URLs for views
        self.user_list_url = reverse('user_list')
        self.user_create_url = reverse('user_add')

    def test_custom_user_creation_form_valid_data(self):
        """
        Test the CustomUserCreationForm with valid data.
        """
        form_data = {
            'email': 'testuser@example.com',
            'email2': 'testuser@example.com',
            'is_staff': True,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(),
                        msg='Form should be valid with correct data.')

        # Save the form and verify the user was created
        user = form.save()
        self.assertEqual(user.email, 'testuser@example.com',
                         msg='Email mismatch.')
        self.assertTrue(user.is_staff, msg='User should be staff.')
        self.assertTrue(user.groups.filter(name='Admin Group').exists(),
                        msg='User not added to Admin Group.')

    def test_custom_user_creation_form_invalid_email_mismatch(self):
        """
        Test the CustomUserCreationForm with mismatched emails.
        """
        form_data = {
            'email': 'testuser@example.com',
            'email2': 'mismatch@example.com',
            'is_staff': True,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid(),
                         msg='Form should be invalid with mismatched emails.')
        self.assertIn('email2', form.errors,
                      msg='Expected email2 error for mismatched emails.')

    def test_custom_user_creation_form_duplicate_email(self):
        """
        Test the CustomUserCreationForm with a duplicate email.
        """
        baker.make(User, email='duplicate_user@example.com')
        form_data = {
            'email': 'duplicate_user@example.com',
            'email2': 'duplicate_user@example.com',
            'is_staff': False,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid(),
                         msg='Form should be invalid for duplicate email.')
        self.assertIn('email2', form.errors,
                      msg='Expected email2 error for duplicate email.')

    def test_custom_user_change_form_non_admin(self):
        """
        Test the CustomUserChangeForm for a non-admin user.
        """
        non_admin_user = baker.make(User, is_staff=False)
        form = CustomUserChangeForm(
            instance=non_admin_user, current_user=self.admin_user)

        self.assertIn('is_staff', form.fields,
                      msg='Admin should see the is_staff field.')

        # Simulate a non-admin user modifying their own details
        non_admin_user_current = baker.make(User, is_staff=False)
        form = CustomUserChangeForm(
            instance=non_admin_user_current,
            current_user=non_admin_user_current)

        self.assertNotIn('is_staff', form.fields,
                         msg='Non-admin should not see the is_staff field.')

    def test_user_create_view_renders_correctly(self):
        """
        Test that the user create view renders the form correctly.
        """
        response = self.client.get(self.user_create_url)

        # Check for 200 OK status
        self.assertEqual(response.status_code, 200,
                         msg='Response NOT OK for user create view.')
        self.assertTemplateUsed(
            response, 'users/user_form.html')
        self.assertIn('form', response.context,
                      msg='Form not in response context.')

    def test_user_create_view_submission(self):
        """
        Test submitting the user creation form through the view.
        """
        data = {
            'email': 'newuser@example.com',
            'email2': 'newuser@example.com',
            'is_staff': True,
        }
        response = self.client.post(self.user_create_url, data)

        # Check for redirect after successful submission
        self.assertEqual(response.status_code, 302,
                         msg='Redirect NOT OK for user create view.')
        self.assertTrue(User.objects.filter(
            email='newuser@example.com').exists(), msg='User not created.')
        self.assertTrue(User.objects.get(
            email='newuser@example.com').groups.filter(
                name='Admin Group').exists(),
            msg='User not added to Admin Group.')

    def test_user_create_view_invalid_submission(self):
        """
        Test submitting the user creation form with invalid data.
        """
        data = {
            'email': 'newuser@example.com',
            'email2': 'mismatch@example.com',
            'is_staff': True,
        }
        response = self.client.post(self.user_create_url, data)

        # Check that the response re-renders the form with errors
        self.assertEqual(response.status_code, 200,
                         msg='Invalid form should re-render.')
        self.assertIn('email2', response.context['form'].errors,
                      msg='Expected email2 error for mismatched emails.')
