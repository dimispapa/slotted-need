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
    path('setup-password/<uidb64>/<token>/',
         CustomPasswordSetupConfirmView.as_view(),
         name='set_password_confirm'),
    path('password-reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='user_reset_password'),
]
