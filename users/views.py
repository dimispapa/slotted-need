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
    # model = User
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

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        # check if to allow edit
        if (request.user.is_superuser or
            (request.user.is_staff and not user.is_staff) or
                request.user == user):
            return super().dispatch(request, *args, **kwargs)
        # otherwise notify that it is not allowed
        else:
            messages.error(request, 'You cannot edit this user.')
            return redirect('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User updated successfully.')
        return response


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        # check if to allow for deletion
        if (request.user.is_superuser or
            (request.user.is_staff and not user.is_staff) or
                request.user == user):
            return super().dispatch(request, *args, **kwargs)
        # otherwise notify that it is not allowed
        else:
            messages.error(request, 'You cannot delete this user.')
            return redirect('user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
