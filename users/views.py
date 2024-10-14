from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views import View
import os
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import (CustomUserCreationForm, CustomUserChangeForm,
                    CustomPasswordSetupForm)
if os.path.isfile('env.py'):
    import env  # noqa


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
        # Set user as inactive
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        form.save_m2m()

        # Send account setup email (invitation)
        # using a custom passowrd setup form
        email = form.cleaned_data['email']
        reset_form = CustomPasswordSetupForm({'email': email})
        if reset_form.is_valid():
            try:
                reset_form.save(
                    request=self.request,
                    use_https=self.request.is_secure(),
                    email_template_name='users/account_setup_email.html',
                    subject_template_name='users/account_setup_subject.txt',
                    from_email=os.environ.get("DEFAULT_EMAIL"),
                    extra_email_context={
                        'user': user,
                    },
                )
                messages.success(self.request,
                                 'User added successfully. An invitation email'
                                 ' has been sent for account setup.')

            except Exception as e:
                print(f"Error sending email: {e}")
                messages.error(
                    self.request, 'Error sending account setup email.')

        else:
            messages.error(self.request, 'Error sending account setup email.')

        return super().form_valid(form)


class ResendInviteView(LoginRequiredMixin, AdminUserRequiredMixin, View):
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        # check if user has already activated their account
        if user.is_active:
            messages.warning(request, 'This user is already active.')
            return redirect('user_list')

        # Resend the account setup email
        reset_form = CustomPasswordSetupForm({'email': user.email})
        if reset_form.is_valid():
            try:
                reset_form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='users/account_setup_email.html',
                    subject_template_name='users/account_setup_subject.txt',
                    from_email=os.environ.get("DEFAULT_EMAIL"),
                    extra_email_context={
                        'user': user,
                    },
                )
                messages.success(request, 'Invitation email has been resent '
                                 f'to {user.email}.')

            except Exception as e:
                print(f"Error sending email: {e}")
                messages.error(request, 'Error resending account setup email.')
        else:
            messages.error(request, 'Invalid form submission.')

        return redirect('user_list')


class CustomPasswordSetupConfirmView(PasswordResetConfirmView):
    template_name = 'users/account_setup_confirm.html'
    success_url = reverse_lazy('account_login')

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
            'Your password has been set successfully. You can now log in.')
        return response


class UserUpdateView(LoginRequiredMixin, AdminUserRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    extra_context = {'title': 'Edit User'}

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser and not request.user.is_superuser:
            messages.error(request, 'You cannot edit this user.')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

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
        if (not (request.user.is_staff or user == request.user)
                or user.is_superuser):
            messages.error(request, 'You cannot delete this user.')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
