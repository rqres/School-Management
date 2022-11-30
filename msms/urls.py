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
    path("sign_up", views.sign_up, name="sign_up"),  # path for the signup page
    path(
        "sign_up/student", views.sign_up_student, name="sign_up_student"
    ),  # path for the student sign-up page
    path("log_in", views.log_in, name="log_in"),  # path to log-in page
    path("log_out", views.log_out, name="log_out"), # path to log-out page
    # todo: add path to account overview
    # path("account", views.account, name="account")
    path(
        "account/bookings", views.bookings_list, name="bookings_list"
    ),  # path to view my bookings
    path(
        "account/requests", views.requests_list, name="requests_list"
    ),  # path to view my requests for lessons
    path(
        "account/requests/create", views.create_request, name="create_request"
    ),  # path to create new request'
    path(
        "admininteractions", views.admininteractions, name="admininteractions"
    ), #admins go on here to login
    path("admininteractions/log_in_admin", views.log_in_admin, name="log_in_admin") #path to admin login page
]
