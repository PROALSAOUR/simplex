from django.urls import path
from .views import *

app_name = "management"

urlpatterns = [
    path('', admins_dashboard, name='admins_dashboard'),
    path('stores/all/', show_stores, name='show_stores'),
    path('store-list/<int:sid>/', store_list, name='store_list'),
    
    path('review/', review_center, name='review_center'),
    path('review/stores/', stores_to_review, name='stores_to_review'),
    path('review/products/', products_to_review, name='products_to_review'),
    path('review/orders/', orders_to_review, name='orders_to_review'),
    path('review/invoices/', invoices_to_review, name='invoices_to_review'),
    path('review/invoice/<int:rid>/', invoice_details, name='invoice_details'),
    path('edit/invoice/<int:rid>/', edit_invoice, name='edit_invoice'),
    
    path('stores/<int:store_id>/billing/', store_billing, name='store_billing'),
    path('stores/billing-management/', billing_management, name='billing_management'),
    path('stores/<int:store_id>/statistics/', store_statistics, name='store_statistics'),

]