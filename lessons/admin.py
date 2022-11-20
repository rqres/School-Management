from django.contrib import admin
from django.contrib.auth.models import Group

# from .models import Student
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from lessons.models import User, Booking

# Register your models here.


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("email", "first_name", "last_name", "is_admin", "is_student")
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_student",
                )
            },
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

# @admin.register(Student)
# class UserAdmin(admin.ModelAdmin):
#     list_display = [
#         "email",
#         "first_name",
#         "last_name",
#         "is_active",
#     ]

# Admin can edit bookings and create them
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("student","startTime","endTime","invoice")
    # TODO: Have a function to view invoice of that Booking
    def view_invoice_link(self, obj):
        pass