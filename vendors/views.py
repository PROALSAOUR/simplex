from django.shortcuts import render

def vendor_dashboard(request):
    return render(request, 'vendors/vendor_dashboard.html')