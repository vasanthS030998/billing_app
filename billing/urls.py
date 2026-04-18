from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("",                          views.billing_form,     name="billing_form"),
    path("generate/",                 views.generate_bill,    name="generate_bill"),
    path("bill/<int:purchase_id>/",   views.bill_view,        name="bill_view"),
    path("history/",                  views.purchase_history, name="purchase_history"),
    path("history/<int:purchase_id>/",views.purchase_detail,  name="purchase_detail"),
    path("api/product/",              views.get_product_info, name="get_product_info"),
]