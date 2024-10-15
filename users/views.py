from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views import View
import os
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import (CustomUserCreationForm,
                    CustomUserChangeForm,)
from .utils import send_invitation_email
if os.path.isfile('env.py'):
    import env  # noqa
import logging

logger = logging.getLogger(__name__)


class AdminUserRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure the user is an admin."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request,
                       'You do not have permission to access this page.')
        return redirect('account_login')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'


class UserCreateView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    extra_context = {'title': 'Add User'}

    def form_valid(self, form):
        # Extract form data without saving to commit=False
        user = form.save(commit=False)
        # Set username to email
        user.username = user.email
        # User is inactive until they set their password
        user.is_active = False
        # Prevent login until password is set
        user.set_unusable_password()
        user.save()

        # Send the invitation email using the utility function
        success, error = send_invitation_email(user, self.request)
        if success:
            messages.success(self.request,
                             'User added successfully. An invitation email '
                             'has been sent for account setup.')
        else:
            messages.error(
                self.request, 'Error sending account setup email.')
            logger.error(
                "UserCreateView: "
                F"Failed to send invitation email to {user.email}: {error}")

        return redirect(self.success_url)


class ResendInviteView(LoginRequiredMixin, AdminUserRequiredMixin, View):
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)

        # Check if user has already activated their account
        if user.is_active:
            messages.warning(request, 'This user is already active.')
            logger.warning(
                f"SendInviteView: User {user.email} is already active.")
            return redirect('user_list')

        # Send the invitation email using the utility function
        success, error = send_invitation_email(user, request)
        if success:
            messages.success(
                request,
                f'Invitation email has been sent to {user.email}.')
        else:
            messages.error(request,
                           'Error sending account setup email.')
            logger.error(
                "SendInviteView: Failed to send invitation email to"
                f" {user.email}: {error}")

        return redirect('user_list')


class PasswordSetupConfirmView(PasswordResetConfirmView):
    template_name = 'users/account_setup_confirm.html'
    success_url = reverse_lazy('account_login')
    # form_class = PasswordSetupForm

    def form_valid(self, form):
        # Save the new password
        response = super().form_valid(form)

        # Activate the user
        user = form.user  # Access the user instance
        user.is_active = True
        user.save()

        # Add a success message
        messages.success(
            self.request,
            'Your password has been set successfully. You are now logged in.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = self.validlink
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    extra_context = {'title': 'Edit User'}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the current user to the form
        kwargs['current_user'] = self.request.user
        return kwargs

    def test_func(self):
        """
        Determine if the current user has permission to update the target user.
        Superusers can update admins and normal users, except other superusers.
        Admins can update normal users but not other admins or superusers.
        Non-admins can only update themselves.
        """
        user = self.request.user
        target_user = self.get_object()
        # return true or false depending if any of these conditions is met
        return ((user.is_staff and not target_user.is_staff) or
                user == target_user or
                user.is_superuser and not target_user.is_superuser)

    def form_valid(self, form):
        """
        Ensure that non-admin users cannot modify the 'is_staff' field.
        Even if they manipulate the form data to include 'is_staff',
        this method will prevent it from being saved.
        """
        if not self.request.user.is_staff:
            # Preserve the original 'is_staff' status
            form.instance.is_staff = self.get_object().is_staff
        return super().form_valid(form)

    def handle_no_permission(self):
        """
        Handle cases where the user doesn't have permission to access the view.
        """
        messages.error(self.request,
                       'You do not have permission to edit this user.')
        return redirect('user_list')


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        """
        Determine if the current user has permission to delete the target user.
        Superusers can delete admins and normal users, except other superusers.
        Admins can delete normal users but not other admins or superusers.
        Non-admins can only delete themselves.
        """
        user = self.request.user
        target_user = self.get_object()
        # return true or false depending if any of these conditions is met
        return ((user.is_staff and not target_user.is_staff) or
                user == target_user or
                user.is_superuser and not target_user.is_superuser)

    def handle_no_permission(self):
        """
        Handle cases where the user doesn't have permission to access the view.
        """
        messages.error(self.request,
                       'You do not have permission to delete this user.')
        return redirect('user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
