from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=200)
    product_id = models.CharField(max_length=100, unique=True)
    available_stocks = models.PositiveIntegerField(default=0)
    unit_price = models.FloatField()
    tax_percentage = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.product_id} - {self.name}"

    class Meta:
        ordering = ["name"]


class Purchase(models.Model):
    customer_email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    total_price_without_tax = models.FloatField(default=0.0)
    total_tax_payable = models.FloatField(default=0.0)
    net_price = models.FloatField(default=0.0)
    rounded_net_price = models.FloatField(default=0.0)
    cash_paid = models.FloatField(default=0.0)
    balance_payable = models.FloatField(default=0.0)
    denomination_input = models.JSONField(default=dict)   # counts submitted by cashier
    balance_denomination = models.JSONField(default=dict) # change returned to customer

    def __str__(self):
        return f"Purchase #{self.pk} - {self.customer_email}"

    class Meta:
        ordering = ["-created_at"]


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price_at_purchase = models.FloatField()
    tax_percentage_at_purchase = models.FloatField()
    purchase_price = models.FloatField()   # unit_price × quantity
    tax_payable = models.FloatField()      # purchase_price × tax_pct / 100
    total_price = models.FloatField()      # purchase_price + tax_payable

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"