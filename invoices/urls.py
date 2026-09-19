from django.urls import path
from .views import *

app_name = "invoices"

urlpatterns = [
    path('view/all/', all_stores_invoices, name='all_stores_invoices'),
    
    path('store/<int:sid>/all/', store_invoices, name='store_invoices'),
    path('invoice/<int:rid>/', view_invoice, name='view_invoice'),
    path('edit/invoice/<int:rid>/', edit_invoice, name='edit_invoice'),
    
    path('stores/<int:sid>/statistics/', store_statistics, name='store_statistics'),
]