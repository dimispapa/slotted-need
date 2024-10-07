from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import CustomUserCreationForm, CustomUserChangeForm


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


class UserCreateView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    extra_context = {'title': 'Add User'}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User added successfully.')
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


class UserDeleteView(LoginRequiredMixin, AdminUserRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser or user == request.user:
            messages.error(request, 'You cannot delete this user.')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)
