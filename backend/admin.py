from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from api.models import ApplicationUser

# Register your models here.
admin.site.register(ApplicationUser, UserAdmin)

admin.site.unregister(Group)
