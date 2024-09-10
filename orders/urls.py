from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    # renders create_order.html template
    path('create-order/', views.create_order, name="create_order"),
    # get_products API
    path('api/get_products/', views.get_products, name='get_products'),
    # get_product_options API, with product_id as a path parameter
    path('api/get_product_data/<int:product_id>/',
         views.get_product_data, name='get_product_data'),
    # get_component_finishes API, with option_value_id as a path parameter
    path('api/get_component_finishes/<int:option_value_id>/',
         views.get_component_finishes, name='get_component_finishes'),
    # search_clients API, with client_name as a query parameter set in the view
    path('api/search_clients/', views.search_clients, name='search_clients')
]
