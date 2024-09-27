from . import views
from django.urls import path

urlpatterns = [
    # ****** URL template section ***********
    # render the home.html template dashboard
    path('', views.home, name='home'),
    # renders create_order.html template
    path('create-order/', views.create_order, name="create_order"),
    # renders orders.html template
    path('order-tracker/', views.OrderListView.as_view(),
         name="order_tracker"),
    # render order_items.html template list view with filters
    path('order-item-tracker/', views.OrderItemListView.as_view(),
         name='order_item_tracker'),
    # ***** API section ***********
    # get_products API
    path('api/get-products/', views.get_products, name='get_products'),
    # get_product_options API, with product_id as a path parameter
    path('api/get-product-data/<int:product_id>/',
         views.get_product_data, name='get_product_data'),
    # get_finishes API, with option_value_id as a path parameter
    path('api/get-finishes/<int:product_id>/<int:option_value_id>/',
         views.get_finishes, name='get_finishes'),
    # check_client API (uses a post request to pass client form data)
    path('api/check-client/', views.check_client, name='check_client'),
    # search_clients API, with client_name as a query parameter set in the view
    path('api/search-clients/', views.search_clients, name='search_clients'),
    # delete_order API, with order_id as path parameters
    path('api/delete-order/<int:order_id>/', views.delete_order,
         name='delete_order'),
    # get order details API, with order_id as path parameter
    path('api/<int:order_id>/details/',
         views.order_details, name='order_details'),
    # update paid status API
    path('api/update_paid_status/',
         views.update_paid_status, name='update_paid_status'),
]
