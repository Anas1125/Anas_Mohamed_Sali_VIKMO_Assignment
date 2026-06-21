import json
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .models import Dealer
from .serializers import DealerSerializer
from .models import Inventory
from .serializers import InventorySerializer
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderItemSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['get','post'])
    def confirm(self, request, pk=None):

        order = self.get_object()

        if order.status != "DRAFT":
            return Response({
                "error": "Only draft orders can be confirmed"
            }, status=400)

        with transaction.atomic():

            for item in order.items.all():

                inventory = Inventory.objects.select_for_update().get(
                    product=item.product
                )

                if inventory.quantity < item.quantity:
                    return Response({
                        "error": (
                            f"Insufficient stock for {item.product.name}. "
                            f"Available: {inventory.quantity}, "
                            f"Requested: {item.quantity}"
                        )
                    }, status=400)
                inventory.quantity -= item.quantity
                inventory.save()

            order.status = "CONFIRMED"
            order.save()
            return Response({
                "message": "Order confirmed successfully"
            })
        
    @action(detail=True, methods=['get','post'])
    def deliver(self, request, pk=None):
        order = self.get_object()

        if order.status != "CONFIRMED":
            return Response({
                "error": "Only confirmed orders can be delivered"
            }, status=400)

        order.status = "DELIVERED"
        order.save()

        return Response({
            "message": "Order delivered successfully"
        })

    def update(self, request, *args, **kwargs):

        order = self.get_object()

        if order.status != "DRAFT":
            return Response(
                {
                    "error": "Confirmed or delivered orders cannot be edited"
                },
                status=400
            )

        return super().update(
            request,
            *args,
            **kwargs
        )
    def destroy(self, request, *args, **kwargs):

        order = self.get_object()

        if order.status != "DRAFT":
            return Response(
                {
                    "error": "Confirmed or delivered orders cannot be deleted"
                },
                status=400
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

@api_view(["GET", "POST"])
def sync_channel(request):

    file_path = Path("channel_feed.json")

    with open(file_path, "r") as f:
        products = json.load(f)

    created = 0
    updated = 0

    for item in products:

        product, was_created = Product.objects.update_or_create(
            sku=item["sku"],
            defaults={
                "external_id": item["external_id"],
                "name": item["name"],
                "category": item["category"],
                "price": item["price"]
            }
        )

        Inventory.objects.update_or_create(
            product=product,
            defaults={
                "quantity": item["stock"]
            }
        )

        if was_created:
            created += 1
        else:
            updated += 1

    return Response({
        "created": created,
        "updated": updated
    })