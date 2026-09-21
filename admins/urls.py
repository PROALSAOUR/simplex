from django.urls import path
from .views import *

app_name = "admins"

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('all/stores/', all_stores, name='all_stores'),
    path('all/orders/', all_orders, name='all_orders'),
    path('all/products/', all_products, name='all_products'),
    path('all/invoices/', all_invoices, name='all_invoices'),
    path('store-list/<int:sid>/', store_list, name='store_list'),
    

]