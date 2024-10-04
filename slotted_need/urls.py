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
from orders.apis import router
from .views import UserListView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/', include(router.urls)),
    # Frontend views
    path('', include('orders.urls'), name='orders-urls'),
    # DRF Authentication
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # User access management
    path('users/', UserListView.as_view(), name='user_list'),
]
