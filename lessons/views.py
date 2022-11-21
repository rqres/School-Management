from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from .forms import StudentSignUpForm
from .forms import LogInForm
from .models import Booking

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
    form = LogInForm()
    return render(request, "log_in.html", {"form": form})

@login_required
def booking_list(request):
    bookings = Booking.objects.all() # Gets all existing booking not specific to user logged in
    return render(request, 'booking_list.html', {'bookings': bookings})
    
@login_required
def show_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except ObjectDoesNotExist:
        return redirect('bookings')
    else:
        return render(request, 'show_booking.html', {'booking' : booking})