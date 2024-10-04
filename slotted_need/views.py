from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView


class AdminUserRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure the user is an admin."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request,
                       'You do not have permission to access this page.')
        return redirect('login')


class UserListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
