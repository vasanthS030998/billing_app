from django.core.management.base import BaseCommand
from billing.models import Product


SAMPLE_PRODUCTS = [
    {"name": "Rice (1 kg)",      "product_id": "P001", "unit_price": 60.00,  "tax_percentage": 0.0,  "available_stocks": 100},
    {"name": "Cooking Oil (1L)", "product_id": "P002", "unit_price": 180.00, "tax_percentage": 5.0,  "available_stocks": 50},
    {"name": "Sugar (1 kg)",     "product_id": "P003", "unit_price": 45.00,  "tax_percentage": 0.0,  "available_stocks": 80},
    {"name": "Wheat Flour (1kg)","product_id": "P004", "unit_price": 55.00,  "tax_percentage": 0.0,  "available_stocks": 60},
    {"name": "Milk (1L)",        "product_id": "P005", "unit_price": 25.00,  "tax_percentage": 0.0,  "available_stocks": 200},
    {"name": "Shampoo (200ml)",  "product_id": "P006", "unit_price": 120.00, "tax_percentage": 18.0, "available_stocks": 30},
    {"name": "Soap Bar",         "product_id": "P007", "unit_price": 35.00,  "tax_percentage": 12.0, "available_stocks": 150},
    {"name": "Biscuits (Pack)",  "product_id": "P008", "unit_price": 20.00,  "tax_percentage": 5.0,  "available_stocks": 300},
    {"name": "Tea (100g)",       "product_id": "P009", "unit_price": 80.00,  "tax_percentage": 5.0,  "available_stocks": 70},
    {"name": "Coffee (100g)",    "product_id": "P010", "unit_price": 150.00, "tax_percentage": 5.0,  "available_stocks": 40},
]


class Command(BaseCommand):
    help = "Seed sample products into the database"

    def handle(self, *args, **kwargs):
        created = 0
        for data in SAMPLE_PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                product_id=data["product_id"],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} new product(s). Total: {Product.objects.count()}"
        ))