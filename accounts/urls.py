from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('', account_list, name='account_list'), 
    path('account_details/', account_details, name='account_details'), 
    path('edit/account-details/', edit_account_details, name='edit_account_details'), 
    path('store-details/', store_details, name='store_details'), 
    path('edit/store-details/', edit_store_details, name='edit_store_details'), 
    path('store-details/add/employee/', add_employee, name='add_employee'), 
    path('log-in/', log_in, name='log_in'),
    path('sign-up/', sign_up, name='sign_up'),
    path('log-out/', log_out, name='log_out'),
    path('check-username/', check_username, name='check_username'),
    path('account-under-review/', account_under_review, name='account_under_review'),
]