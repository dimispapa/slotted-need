from django.urls import path
from .views import UserListView, UserCreateView, UserUpdateView, UserDeleteView

urlpatterns = [
    # User access management
    path('', UserListView.as_view(), name='user_list'),
    path('add/', UserCreateView.as_view(), name='user_add'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('delete/<int:pk>/', UserDeleteView.as_view(),
         name='user_delete'),
]
