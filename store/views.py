from django.shortcuts import render


def store_dashboard(request):
    return render(request, 'store/dashboard.html')
