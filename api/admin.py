from django.contrib import admin
from django.urls import path
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from api.models import Buoy, Parameter, Data, ActionItems, ApplicationUser, News
from api.forms import BuoyForm


# Register your models here.

class BuoyAdmin(admin.ModelAdmin):
    form = BuoyForm


    # def get_urls(self):
    #     urls = super().get_urls()
    #     my_urls = [path("add/", self.admin_site.admin_view(self.my_view))]
    #     return my_urls + urls

    # def my_view(self, request):
    #     # ...
    #     context = dict(
    #         # Include common variables for rendering the admin template.
    #         self.admin_site.each_context(request),
    #         # Anything else you want in the context...
    #         # key=value,
    #     )
    #     return TemplateResponse(request, "create_buoy.html", context)


class ParameterAdmin(admin.ModelAdmin):
    fields = ['fullname', 'description', 'min', 'max', 'uom', 'active']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DataAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ActionItemsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class NewsAdmin(admin.ModelAdmin):
    fields = ['title', 'content']


admin.site.unregister(ApplicationUser)


@admin.register(ApplicationUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "company", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                ),
            },
        ),
    )

admin.site.register(Buoy, BuoyAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(ActionItems, ActionItemsAdmin)
admin.site.register(News, NewsAdmin)