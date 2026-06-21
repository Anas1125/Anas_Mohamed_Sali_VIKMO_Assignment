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

from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>VIKMO Dashboard</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: white;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 50px;
            }

            h1 {
                text-align: center;
                font-size: 48px;
                margin-bottom: 10px;
            }

            .subtitle {
                text-align: center;
                color: #cbd5e1;
                margin-bottom: 50px;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
            }

            .card {
                background: rgba(255,255,255,0.08);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                text-decoration: none;
                color: white;
                transition: 0.3s;
                backdrop-filter: blur(10px);
            }

            .card:hover {
                transform: translateY(-8px);
                background: rgba(255,255,255,0.15);
            }

            .icon {
                font-size: 40px;
                margin-bottom: 10px;
            }

            .title {
                font-size: 22px;
                font-weight: bold;
            }

            .desc {
                color: #cbd5e1;
                margin-top: 8px;
                font-size: 14px;
            }

            .footer {
                text-align: center;
                margin-top: 50px;
                color: #94a3b8;
            }
        </style>
    </head>
    <body>

        <div class="container">

            <h1>🚀 VIKMO Dashboard</h1>

            <p class="subtitle">
                Sales Order & Inventory Management System
            </p>

            <div class="grid">

                <a href="/admin/" class="card">
                    <div class="icon">⚙️</div>
                    <div class="title">Admin</div>
                    <div class="desc">Manage system data</div>
                </a>

                <a href="/api/products/" class="card">
                    <div class="icon">📦</div>
                    <div class="title">Products</div>
                    <div class="desc">View all products</div>
                </a>

                <a href="/api/inventory/" class="card">
                    <div class="icon">📊</div>
                    <div class="title">Inventory</div>
                    <div class="desc">Track stock levels</div>
                </a>

                <a href="/api/dealers/" class="card">
                    <div class="icon">🏪</div>
                    <div class="title">Dealers</div>
                    <div class="desc">Manage dealers</div>
                </a>

                <a href="/api/orders/" class="card">
                    <div class="icon">🛒</div>
                    <div class="title">Orders</div>
                    <div class="desc">Process orders</div>
                </a>

                <a href="/api/sync/channel/" class="card">
                    <div class="icon">🔄</div>
                    <div class="title">Channel Sync</div>
                    <div class="desc">Sync external products</div>
                </a>

            </div>

            <div class="footer">
                Built with Django REST Framework | Anas Mohamed
            </div>

        </div>

    </body>
    </html>
    """)

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

                print(
                    f"ORDER={order.id}, "
                    f"PRODUCT={item.product.id}, "
                    f"QTY={item.quantity}"
                )

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

@api_view(["POST"])
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