from django.urls import path
from .views import *

app_name = "management"

urlpatterns = [
    path('', admins_dashboard, name='admins_dashboard'),
    path('review_center/', review_center, name='review_center'),
    path('all/stores/', show_stores, name='show_stores'),
    path('stores/review/', stores_to_review, name='stores_to_review'),
    path('stores/products/review/', products_to_review, name='products_to_review'),
    path('stores/orders/review/', orders_to_review, name='orders_to_review'),
    path('stores/<int:sid>/', store_list, name='store_list'),

]