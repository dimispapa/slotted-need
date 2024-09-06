from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('create-order/', views.create_order, name="create_order"),
    path('api/get_options_data/', views.get_options_data,
         name='get_options_data'),
    path('api/search_clients/', views.search_clients, name='search_clients')
]
