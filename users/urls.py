from django.urls import path
from .views import (UserListView, UserCreateView, UserUpdateView,
                    UserDeleteView, PasswordSetupConfirmView,
                    ResendInviteView)

urlpatterns = [
    # User access management
    path('', UserListView.as_view(), name='user_list'),
    # user add view
    path('add/', UserCreateView.as_view(), name='user_add'),
    # user update view
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    # user delete view
    path('delete/<int:pk>/', UserDeleteView.as_view(),
         name='user_delete'),
    # Resend Invite
    path('resend-invite/<int:user_id>/', ResendInviteView.as_view(),
         name='resend_invite'),
    # Account Setup Confirmation
    path(
        'confirm-account-setup/<uidb64>/<token>/',
        PasswordSetupConfirmView.as_view(),
        name='account_setup_confirm'
    ),
]
