from django.urls import path
from .views import (UserListView, UserCreateView, UserUpdateView,
                    UserDeleteView, CustomPasswordSetupConfirmView,
                    CustomPasswordResetConfirmView,)

# app_name = 'users'

urlpatterns = [
    # User access management
    path('', UserListView.as_view(), name='user_list'),
    path('add/', UserCreateView.as_view(), name='user_add'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('delete/<int:pk>/', UserDeleteView.as_view(),
         name='user_delete'),
    path('confirm-password-reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='confirm_password_reset'),

    # Account Setup URLs (used when a new user is created)
    path('confirm-account-setup/<uidb64>/<token>/',
         CustomPasswordSetupConfirmView.as_view(),
         name='account_setup_confirm'),
]
