from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('create-order/', views.create_order, name="create_order"),
]
