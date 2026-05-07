from django.urls import path
from .views import *

app_name = 'store'

urlpatterns = [
    path('', store_dashboard, name='store_dashboard'), 
    path('products/', show_products, name='show_products'), 
    path('products/add/', add_product, name='add_product'), 
    path('products/edit/<int:pid>', edit_product, name='edit_product'), 
    path('products/view/<int:pid>', view_product, name='view_product'), 
    path('products/delete/', delete_product, name='delete_product'), 
]