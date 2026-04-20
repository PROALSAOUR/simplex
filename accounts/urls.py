from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('', account_list, name='account_list'), 
    path('account_details/', account_details, name='account_details'), 
    path('edit/account-details/', edit_account_details, name='edit_account_details'), 
    path('store-details/', store_details, name='store_details'), 
    
    path('store/edit/basic/', edit_store_basic, name='edit_store_basic'), 
    path('store/edit/social/', edit_store_social, name='edit_store_social'), 
    path('store/edit/logo/', edit_store_logo, name='edit_store_logo'), 
    
    
    
    
    
    path('store-details/add/employee/', add_employee, name='add_employee'), 
    path('store-details/remove/employee/', remove_employee, name='remove_employee'), 
    path('store-details/edit/employee/', edit_employee, name='edit_employee'), 
    path('log-in/', log_in, name='log_in'),
    path('sign-up/', sign_up, name='sign_up'),
    path('log-out/', log_out, name='log_out'),
    path('check-username/', check_username, name='check_username'),
    path('account-under-review/', account_under_review, name='account_under_review'),
]