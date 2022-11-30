from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from lessons.models import Booking, RequestForLessons
from .forms import RequestForLessonsForm, StudentSignUpForm, AdminLoginForm, LogInForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

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

#admins redirected to admin login page
def admininteractions(request):
    return render(request, "log_in_admin.html")

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

def log_in_admin(request):
    if request.method == "POST":
        adminloginform = AdminLoginForm(request.POST)
        if adminloginform.is_valid():
            username = adminloginform.cleaned_data.get('username')
            password = adminloginform.cleaned_data.get('password')
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(home)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid.")
    adminloginform = AdminLoginForm()
    return render(request, "log_in_admin.html", {"form": adminloginform})

def log_out(request):
    logout(request)
    return redirect(home)


@login_required
def bookings_list(request):
    bookings = Booking.objects.filter(student=request.user)
    return render(request, "bookings_list.html", {"bookings": bookings})


@login_required
def requests_list(request):
    requests = RequestForLessons.objects.filter(student=request.user)
    return render(request, "requests_list.html", {"requests": requests})


@login_required
def create_request(request):
    if request.method == "POST":
        form = RequestForLessonsForm(request.POST, usr=request.user)
        if form.is_valid():
            req = form.save()
            print(req)
            return redirect("home")

    form = RequestForLessonsForm(usr=request.user)
    return render(request, "create_request.html", {"form": form})
