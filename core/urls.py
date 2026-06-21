from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, DealerViewSet

router = DefaultRouter()
router.register(
    r'products',
    ProductViewSet
)

urlpatterns = router.urls
router = DefaultRouter()
router.register(
    r'products',
    ProductViewSet
)

router.register(
    r'dealers',
    DealerViewSet
)

urlpatterns = router.urls