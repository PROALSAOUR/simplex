from django.urls import path
from .views import *

app_name = 'orders'

urlpatterns = [
    path('<int:sid>/', show_orders, name='show_orders'), 
    path('edit/<int:oid>', edit_order, name='edit_order'), 
    path('add/', add_order, name='add_order'), 
    path('add/manually/', add_order_manually, name='add_order_manually'), 
    
    path('order-item/<int:item_id>/delete/', delete_order_item, name='delete_order_item'),
    path('<int:oid>/add/order-item/', add_order_item, name='add_order_item'),
]
