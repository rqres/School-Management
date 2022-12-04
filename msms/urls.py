"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from lessons import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),  # path for the home page

    # ---------- LOG IN SECTION ----------
    path("log_in/", views.log_in, name="log_in"),  # path to log-in page
    path("log_out/", views.log_out, name="log_out"),  # path to log-out page
    path(
        "forgot_password/", views.forgot_password, name="forgot_password"
    ),  # path to reset password

    # ---------- SIGN UP SECTION ----------
    path("sign_up/", views.sign_up, name="sign_up"),  # path for the signup page
    path(
        "sign_up/student/", views.sign_up_student, name="sign_up_student"
    ),  # path for the student sign-up page

    # ---------- UNIVERSAL ACCOUNT DASHBOARD ----------
    # (all users will be redirected here regardless of usertype)
    path(
<<<<<<< HEAD
        "forgot_password/", views.forgot_password, name="forgot_password"
    ),  # path to reset password

=======
        "account/", views.account, name="account"
    ),  # path to account overview (currently a simple redirect)

    # ---------- USER's BOOKINGS SECTION ----------
>>>>>>> b1a9df92f42c3d1739291c038b4b6c179d345780
    path(
        "account/bookings/", views.bookings_list, name="bookings_list"
    ),  # path to list of bookings
    path(
        "account/bookings/<int:booking_id>/", views.show_booking, name="show_booking"
    ),  # path to show a booking
<<<<<<< HEAD

    path("log_out/", views.log_out, name="log_out"),  # path to log-out page

    path("account/", views.account, name="account"), # path to account overview (currently a simple redirect)

=======

    # ---------- USER's REQUESTS FOR LESSONS SECTION ----------
>>>>>>> b1a9df92f42c3d1739291c038b4b6c179d345780
    path(
        "account/requests/", views.requests_list, name="requests_list"
    ),  # path to view my requests for lessons
    path(
        "account/requests/create/", views.create_request, name="create_request"
    ),  # path to create new request
<<<<<<< HEAD

    path(
        "account/payment/", views.payment, name="payment_form"
    ),# path to payment page
    path(
        "account/requests/create", views.create_request, name="create_request"
    ),  # path to create new request
=======
>>>>>>> b1a9df92f42c3d1739291c038b4b6c179d345780
    path(
        "account/requests/<int:lessons_request_id>/",
        views.show_request,
        name="show_request",
    ),
<<<<<<< HEAD
    path("admininteractions/", views.admininteractions, name="admininteractions"), #admins go on here to login
    path("log_in_admin/", views.log_in_admin, name="log_in_admin"), #path to admin login page
    path("sign_up_admin/", views.sign_up_admin, name="sign_up_admin"),
    path("adminaccount/", views.adminaccount, name="adminaccount"),
=======
    path(
        "account/requests/<int:lessons_request_id>/delete",
        views.delete_request,
        name="delete_request",
    ),
>>>>>>> b1a9df92f42c3d1739291c038b4b6c179d345780

    # ---------- USER's PAYMENT SECTION ----------
    path(
        "account/payment/", views.payment, name="payment_form"
    ),  # path to payment page

    # ---------- ADMIN SECTION ----------
    path(
        "schoolterms/",
        views.school_terms_list,
        name="school_terms_list",
    ),
    path(
        "schoolterms/create/",
        views.create_school_term,
        name="create_school_term",
    ),
]
