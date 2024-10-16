"""
URL configuration for slotted_need project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .apis import router
from .views import (HomeView, ProductRevenueDataAPIView, DebtorBalancesAPIView,
                    ItemStatusProductAPIView, ItemStatusConfigAPIView)
# from users.views import CustomLoginView


urlpatterns = [
    # render the home.html template dashboard
    path('', HomeView.as_view(), name='home'),
    # Admin site
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/product-revenue-data/', ProductRevenueDataAPIView.as_view(),
         name='product_revenue_data'),
    path('api/debtors-data/', DebtorBalancesAPIView.as_view(),
         name='debtors_balances_data'),
    path('api/item-status-product-data/', ItemStatusProductAPIView.as_view(),
         name='item_status_product_data'),
    path('api/item-status-config-data/', ItemStatusConfigAPIView.as_view(),
         name='item_status_config_data'),
    # Order views
    path('orders/', include('orders.urls')),
    # all-auth
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    # User views
    path('users/', include('users.urls')),
]
