from rest_framework import routers
from orders.views import OrderItemViewSet

router = routers.DefaultRouter()
router.register(r'orderitems', OrderItemViewSet)
