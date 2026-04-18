from django.contrib import admin
from .models import Product, Purchase, PurchaseItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ["product_id", "name", "unit_price", "tax_percentage", "available_stocks"]
    search_fields = ["product_id", "name"]
    list_filter   = ["tax_percentage"]
    ordering      = ["name"]


class PurchaseItemInline(admin.TabularInline):
    model         = PurchaseItem
    extra         = 0
    readonly_fields = [
        "product", "quantity", "unit_price_at_purchase",
        "tax_percentage_at_purchase", "purchase_price", "tax_payable", "total_price",
    ]
    can_delete = False


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display  = ["pk", "customer_email", "rounded_net_price", "cash_paid", "balance_payable", "created_at"]
    search_fields = ["customer_email"]
    list_filter   = ["created_at"]
    readonly_fields = [
        "total_price_without_tax", "total_tax_payable", "net_price",
        "rounded_net_price", "balance_payable", "balance_denomination", "denomination_input",
    ]
    inlines = [PurchaseItemInline]