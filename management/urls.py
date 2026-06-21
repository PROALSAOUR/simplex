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
    path('review/invoices/', invoices_to_review, name='invoice_to_review'),
    
    path('stores/<int:store_id>/statistics/', store_statistics, name='store_statistics'),

]