from . import views
from django.urls import path

urlpatterns = [
    path('', views.create_order, name="create_order")
]
