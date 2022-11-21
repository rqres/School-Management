from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from lessons.models import Booking, RequestForLessons, Student
from lessons.forms import RequestForLessonsForm, StudentSignUpForm, LogInForm


#  Create your views here.
def home(request):
    return render(request, "home.html")


def sign_up(request):
    return render(request, "sign_up.html")


def sign_up_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            # create user, add it to db, and log them in
            user = form.save()
            login(request, user)
            return redirect("home")

    else:
        form = StudentSignUpForm()

    return render(request, "sign_up_student.html", {"form": form})


def log_in(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")

    else:
        form = LogInForm()

    return render(request, "log_in.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect("home")


@login_required
def show_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except ObjectDoesNotExist:
        return redirect("bookings_list")
    else:
        return render(request, "show_booking.html", {"booking": booking})


@login_required
def bookings_list(request):
    student = Student.objects.get(user=request.user)
    bookings = Booking.objects.filter(student=student)
    return render(request, "bookings_list.html", {"bookings": bookings})


@login_required
def requests_list(request):
    # TODO: change user to student in requests model
    requests = RequestForLessons.objects.filter(student=request.user)
    return render(request, "requests_list.html", {"requests": requests})


@login_required
def create_request(request):
    if request.method == "POST":
        form = RequestForLessonsForm(request.POST, usr=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")

    else:
        form = RequestForLessonsForm(usr=request.user)

    return render(request, "create_request.html", {"form": form})
