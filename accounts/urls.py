from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('', main_accounts, name='main_accounts'), # احذفها بعدين هلأ مؤقتة بس #change-later
    path('log-in/', log_in, name='log_in'),
    path('sign-up/', sign_up, name='sign_up'),
    path('check-username/', check_username, name='check_username'),
    path('account_under_review/', account_under_review, name='account_under_review'),
]