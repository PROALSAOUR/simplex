"""
URL configuration for Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL
from .views import landing_page

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('', landing_page, name='landing_page'), 
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('invoices/', include('invoices.urls')),
    path('orders/', include('orders.urls')),
    path('account/', include('accounts.urls')),
    path('admins/', include('admins.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()

urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)