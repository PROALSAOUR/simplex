from django.urls import path
from .views import *

app_name = 'orders'

urlpatterns = [
    path('', show_orders, name='show_orders'), 
    path('edit/<int:oid>', edit_order, name='edit_order'), 
    path('add/', add_order_manually, name='add_order_manually'), 
]