from django.urls import path
from .views import invoice_list_create, invoice_detail_update_delete, invoice_item_list_create, \
    invoice_item_detail_update_delete

urlpatterns = [
    path("invoices/", invoice_list_create, name="invoice-list-create"),
    path("invoices/<int:pk>/", invoice_detail_update_delete, name="invoice-detail-update-delete"),
    path("invoice-items/", invoice_item_list_create, name="invoice-item-list-create"),
    path("invoice-items/<int:pk>/", invoice_item_detail_update_delete, name="invoice-item-detail-update-delete"),
]
