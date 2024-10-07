from rest_framework import routers
from orders.views import (OrderItemViewSet, OrderViewSet)


router = routers.DefaultRouter()
router.register(r'order-items', OrderItemViewSet)
router.register(r'orders', OrderViewSet)
