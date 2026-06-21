from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .models import Dealer
from .serializers import DealerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer