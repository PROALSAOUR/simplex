from django.urls import path
from .views import *

app_name = "admins"

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('all/stores/', all_stores, name='all_stores'),
    path('all/orders/', all_orders, name='all_orders'),
    path('all/products/', all_products, name='all_products'),
    path('all/invoices/', all_invoices, name='all_invoices'),
    path('all/cities/', all_cities, name='all_cities'),
    path('city/<int:cid>/edit/', edit_city, name='edit_city'),
    path('city/add/', add_city, name='add_city'),
    path('city/delete/', delete_city, name='delete_city'),
    path('store-list/<int:sid>/', store_list, name='store_list'),
    
]