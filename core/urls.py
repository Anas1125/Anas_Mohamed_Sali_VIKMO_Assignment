from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    DealerViewSet,
    InventoryViewSet,
    OrderViewSet,
    OrderItemViewSet,
    sync_channel
)
from django.urls import path

router = DefaultRouter()

router.register(
    r'products',
    ProductViewSet
)

router.register(
    r'dealers',
    DealerViewSet
)

router.register(
    r'inventory',
    InventoryViewSet
)
router.register(
    r'orders',
    OrderViewSet
)

router.register(
    r'order-items',
    OrderItemViewSet
)

urlpatterns = router.urls
urlpatterns += [
    path(
        "sync/channel/",
        sync_channel
    ),
]