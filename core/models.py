from django.db import models
from datetime import date

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    external_id = models.CharField(max_length=50, null=True, blank=True)

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"
    
class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class Dealer(models.Model):
    dealer_code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    
class Order(models.Model):

    def save(self, *args, **kwargs):

        if not self.order_number:

            today = date.today().strftime("%Y%m%d")

            last_order = Order.objects.filter(
                order_number__startswith=f"ORD-{today}"
            ).count()

            sequence = last_order + 1

            self.order_number = (
                f"ORD-{today}-{sequence:04d}"
            )

        super().save(*args, **kwargs)

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("CONFIRMED", "Confirmed"),
        ("DELIVERED", "Delivered"),
    ]

    order_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.order_number
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    def save(self, *args, **kwargs):

        self.line_total = (
            self.quantity * self.unit_price
        )

        super().save(*args, **kwargs)

        self.order.total_amount = sum(
            item.line_total
            for item in self.order.items.all()
        )

        self.order.save()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    