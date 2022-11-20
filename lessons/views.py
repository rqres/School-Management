from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from lessons.models import Booking
from .forms import StudentSignUpForm
from .forms import LogInForm

# # Create your views here.
def home(request):
    return render(request, "home.html")

def sign_up(request):
    # form = SignUpForm()
    return render(request, "sign_up.html")

def sign_up_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            # create user and add to db
            form.save()
            return redirect("home")
            # login(request, user)
            # return redirect("feed")
    else:
        form = StudentSignUpForm()
    return render(request, "sign_up_student.html", {"form": form})


def log_in(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get(username)
            password = form.cleaned_data.get(password)
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(home) # this will need to be changed to the dashboard in time!
    else:
        form = LogInForm()
        return render(request, "log_in.html", {"form": form})

def log_out(request):
    logout(request)
    return redirect(home)


@login_required
def bookings_list(request):
    bookings = Booking.objects.filter(student=request.user)
    return render(request, "bookings_list.html", {"bookings": bookings})