from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('account/under-review/', account_under_review, name='account_under_review'),
    path('account/details/', account_details, name='account_details'), 
    path('account/edit/details/', edit_account_details, name='edit_account_details'), 
    
    path('store/<int:sid>/details/', store_details, name='store_details'), 


    path('log-in/', log_in, name='log_in'),
    path('sign-up/', sign_up, name='sign_up'),
    path('log-out/', log_out, name='log_out'),
    path('check/username/', check_username, name='check_username'),
    path('check/phone-number/', check_phone_number, name='check_phone_number'),
]