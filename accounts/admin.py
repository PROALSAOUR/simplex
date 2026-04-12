from django.contrib import admin
from .models import UserProfile, Store, Vendor
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Store)
admin.site.register(Vendor)
