from django.urls import path
from .views import *

app_name = 'orders'

urlpatterns = [
    path('<int:sid>/', store_orders, name='store_orders'), 
    path('view/<int:oid>', view_order, name='view_order'), 
    path('add/', add_order, name='add_order'), 
    path('add/manually/', add_order_manually, name='add_order_manually'), 
    
    path('order-item/<int:item_id>/delete/', delete_order_item, name='delete_order_item'),
    path('<int:oid>/add/order-item/', add_order_item, name='add_order_item'),
]
