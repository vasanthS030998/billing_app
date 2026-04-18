from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invoice_email(self, purchase_id):
    """Send invoice email to customer asynchronously."""
    from .models import Purchase
    try:
        purchase = Purchase.objects.prefetch_related("items__product").get(pk=purchase_id)

        items_text = "\n".join([
            f"  {item.product.name} (ID: {item.product.product_id}) | "
            f"Qty: {item.quantity} | Unit: ₹{item.unit_price_at_purchase:.2f} | "
            f"Tax: {item.tax_percentage_at_purchase}% | Total: ₹{item.total_price:.2f}"
            for item in purchase.items.all()
        ])

        balance_text = "\n".join([
            f"  ₹{denom}: {count} note(s)"
            for denom, count in purchase.balance_denomination.items()
            if int(count) > 0
        ]) or "  No change required"

        message = f"""Dear Customer,

Thank you for your purchase!

Purchase ID  : #{purchase.pk}
Date         : {purchase.created_at.strftime('%Y-%m-%d %H:%M')}
Email        : {purchase.customer_email}

--- Items Purchased ---
{items_text}

--- Bill Summary ---
Total (excl. tax)   : ₹{purchase.total_price_without_tax:.2f}
Tax Payable         : ₹{purchase.total_tax_payable:.2f}
Net Price           : ₹{purchase.net_price:.2f}
Rounded Net Price   : ₹{purchase.rounded_net_price:.2f}
Cash Paid           : ₹{purchase.cash_paid:.2f}
Balance Returned    : ₹{purchase.balance_payable:.2f}

--- Balance Denomination ---
{balance_text}

Regards,
Billing System
"""
        send_mail(
            subject=f"Invoice #{purchase.pk} – Thank you for your purchase",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[purchase.customer_email],
            fail_silently=False,
        )
    except Purchase.DoesNotExist:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)