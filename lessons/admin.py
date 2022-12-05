from django.contrib import admin
from django.contrib.auth.models import Group

# from .models import Student
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from lessons.models import (
    Booking,
    SchoolAdmin,
    Invoice,
    RequestForLessons,
    Student,
    User,
)

# Register your models here.


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "email",
        "first_name",
        "last_name",
        "password",
        "is_admin",
        "is_student",
        "is_school_admin"
    )
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_school_admin",
                    "is_student",
                    "is_admin",
                    "is_teacher",
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

admin.site.register(Student)
admin.site.register(SchoolAdmin)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(RequestForLessons)

# @admin.register(Student)
# class UserAdmin(admin.ModelAdmin):
#     list_display = [
#         "email",
#         "first_name",
#         "last_name",
#         "is_active",
#     ]

# Admins can edit bookings and create them
class BookingAdmin(admin.ModelAdmin):
    list_display = ("get_student", "get_teacher", "startTime", "endTime", "invoice")

    def get_student(self, booking):
        """Return student of a given booking"""
        return booking.student.email

    def get_teacher(self, booking):
        """Return student of a given booking"""
        return booking.teacher.email

    # TODO: Have a function to view invoice of that Booking
    def view_invoice_link(self, booking):
        """Return invoice of a given booking"""
        pass
