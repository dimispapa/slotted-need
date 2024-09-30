from rest_framework import routers
from .views import OrderItemViewSet

router = routers.DefaultRouter()
router.register(r'order-items', OrderItemViewSet)
