from django.urls import path
from .views import *

app_name = 'vendors'

urlpatterns = [
    path('', vendor_dashboard, name='vendor_dashboard'), 
]