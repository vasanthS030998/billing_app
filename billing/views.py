import math
import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Product, Purchase, PurchaseItem
from .tasks import send_invoice_email

DENOMINATIONS = [500, 50, 20, 10, 5, 2, 1]


def _calculate_balance_denomination(balance, denomination_counts):
    """Greedy change-making using available denomination counts."""
    remaining = round(balance)
    result = {}
    for denom in sorted([int(k) for k in denomination_counts.keys()], reverse=True):
        available = int(denomination_counts.get(str(denom), 0))
        if remaining <= 0 or available <= 0:
            result[str(denom)] = 0
            continue
        use = min(available, remaining // denom)
        result[str(denom)] = int(use)
        remaining -= use * denom
    return result, remaining


def billing_form(request):
    """Page 1 – Billing entry form."""
    products = Product.objects.filter(available_stocks__gt=0)
    return render(request, "billing/billing_form.html", {
        "products": products,
        "denominations": DENOMINATIONS,
    })


@require_http_methods(["POST"])
def generate_bill(request):
    """Validate, calculate, persist and trigger async email."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body"}, status=400)

    customer_email = data.get("customer_email", "").strip()
    if not customer_email:
        return JsonResponse({"error": "Customer email is required"}, status=400)

    items_data = data.get("items", [])
    if not items_data:
        return JsonResponse({"error": "At least one product item is required"}, status=400)

    denomination_counts = {str(k): int(v) for k, v in data.get("denominations", {}).items()}
    cash_paid = float(data.get("cash_paid", 0))

    # ── Validate items ────────────────────────────────────────────────────────
    validated_items = []
    errors = []
    for idx, item in enumerate(items_data, start=1):
        pid = str(item.get("product_id", "")).strip()
        try:
            qty = int(item.get("quantity", 0))
        except (ValueError, TypeError):
            errors.append(f"Item {idx}: invalid quantity")
            continue

        if not pid:
            errors.append(f"Item {idx}: product ID is required")
            continue
        if qty <= 0:
            errors.append(f"Item {idx}: quantity must be greater than zero")
            continue

        try:
            product = Product.objects.get(product_id=pid)
        except Product.DoesNotExist:
            errors.append(f"Item {idx}: product '{pid}' not found")
            continue

        if product.available_stocks < qty:
            errors.append(
                f"Item {idx}: only {product.available_stocks} unit(s) available for '{product.name}'"
            )
            continue

        validated_items.append((product, qty))

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    # ── Calculate bill ────────────────────────────────────────────────────────
    total_without_tax = 0.0
    total_tax = 0.0
    item_rows = []

    for product, quantity in validated_items:
        purchase_price = round(product.unit_price * quantity, 2)
        tax_payable = round(purchase_price * product.tax_percentage / 100, 2)
        total_price_item = round(purchase_price + tax_payable, 2)
        total_without_tax += purchase_price
        total_tax += tax_payable
        item_rows.append({
            "product": product,
            "quantity": quantity,
            "unit_price": product.unit_price,
            "tax_pct": product.tax_percentage,
            "purchase_price": purchase_price,
            "tax_payable": tax_payable,
            "total_price": total_price_item,
        })

    net_price = round(total_without_tax + total_tax, 2)
    rounded_net_price = math.floor(net_price)
    balance_payable = round(cash_paid - rounded_net_price, 2)

    if balance_payable < 0:
        return JsonResponse(
            {"error": f"Cash paid (₹{cash_paid}) is less than net price (₹{rounded_net_price})"},
            status=400,
        )

    balance_denomination, _ = _calculate_balance_denomination(balance_payable, denomination_counts)

    # ── Persist ───────────────────────────────────────────────────────────────
    purchase = Purchase.objects.create(
        customer_email=customer_email,
        total_price_without_tax=round(total_without_tax, 2),
        total_tax_payable=round(total_tax, 2),
        net_price=net_price,
        rounded_net_price=rounded_net_price,
        cash_paid=cash_paid,
        balance_payable=balance_payable,
        denomination_input=denomination_counts,
        balance_denomination=balance_denomination,
    )

    for row in item_rows:
        PurchaseItem.objects.create(
            purchase=purchase,
            product=row["product"],
            quantity=row["quantity"],
            unit_price_at_purchase=row["unit_price"],
            tax_percentage_at_purchase=row["tax_pct"],
            purchase_price=row["purchase_price"],
            tax_payable=row["tax_payable"],
            total_price=row["total_price"],
        )
        # Deduct stock
        row["product"].available_stocks -= row["quantity"]
        row["product"].save(update_fields=["available_stocks"])

    # ── Async email ───────────────────────────────────────────────────────────
    #send_invoice_email.delay(purchase.pk)
    try:
        send_invoice_email.delay(purchase.pk)
    except Exception:
        pass  

    return JsonResponse({"purchase_id": purchase.pk})


def bill_view(request, purchase_id):
    """Page 2 – Bill receipt."""
    purchase = get_object_or_404(
        Purchase.objects.prefetch_related("items__product"), pk=purchase_id
    )
    balance_denom = {
        int(k): v
        for k, v in purchase.balance_denomination.items()
        if int(v) > 0
    }
    return render(request, "billing/bill_view.html", {
        "purchase": purchase,
        "balance_denom": dict(sorted(balance_denom.items(), reverse=True)),
    })


def purchase_history(request):
    """List all purchases; filter by email."""
    email = request.GET.get("email", "").strip()
    purchases = Purchase.objects.all()
    if email:
        purchases = purchases.filter(customer_email__iexact=email)
    return render(request, "billing/purchase_history.html", {
        "purchases": purchases,
        "email": email,
    })


def purchase_detail(request, purchase_id):
    """Detail of a single historical purchase."""
    purchase = get_object_or_404(
        Purchase.objects.prefetch_related("items__product"), pk=purchase_id
    )
    return render(request, "billing/purchase_detail.html", {"purchase": purchase})


def get_product_info(request):
    """AJAX: return product details by product_id."""
    pid = request.GET.get("product_id", "").strip()
    try:
        p = Product.objects.get(product_id=pid)
        return JsonResponse({
            "name": p.name,
            "unit_price": p.unit_price,
            "tax_percentage": p.tax_percentage,
            "available_stocks": p.available_stocks,
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)