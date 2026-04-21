from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import vendor_only


@login_required(login_url='accounts:log_in')
@vendor_only
def store_dashboard(request):
    return render(request, 'store/dashboard.html')
