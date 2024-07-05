from django.contrib import admin

from .models import UserLibraryAccount,UserAddress
admin.site.register(UserLibraryAccount)
admin.site.register(UserAddress)

