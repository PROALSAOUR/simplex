from django.urls import path
from .views import *

app_name = "management"

urlpatterns = [
    path('', admins_dashboard, name='admins_dashboard'),
    path('review_center/', review_center, name='review_center'),
    path('stores/', show_stores, name='show_stores'),
    path('stores/<int:sid>/', store_list, name='store_list'),
]