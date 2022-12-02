from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RequestForLessonsForm, StudentSignUpForm, PaymentForm,LogInForm, AdminLoginForm, ForgotPasswordForm, SignUpAdminForm
from .models import Booking , Invoice ,RequestForLessons
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

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

#admins redirected to admin login page
def admininteractions(request):
    return render(request, "log_in_admin.html")

def log_in(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("account")
            # TODO: ACCOMODATE DIFFERENT TYPES OF ACCOUNTS (ADMIN, STUDENT, TEACHER, PARENT etc.)
    else:
        form = LogInForm()
    return render(request, "log_in.html", {"form": form})

@login_required
def log_in_admin(request):
    if request.method == "POST":
        adminloginform = AdminLoginForm(request.POST)
        if adminloginform.is_valid():
            email = adminloginform.cleaned_data.get('adminemail')
            password = adminloginform.cleaned_data.get('adminpassword')
            user = authenticate(email= email, password = password)
            if user is not None:
                login(request, user)
                return redirect("adminaccount")
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid.")
    adminloginform = AdminLoginForm()
    return render(request, "log_in_admin.html", {"form": adminloginform})

#check if the user is a director then display sign up page
def sign_up_admin(request):
    if request.method == 'POST':
        form = SignUpAdminForm(request.POST)#creates a bound version of the form with post data
        if form.is_valid():
            user = form.save()
            return redirect('adminaccount')
    else:
        form = SignUpAdminForm()#create a form with SignUpAdminForm constructor, pass that form to template to render it
    return render(request, 'sign_up_admin.html', {'form' : form})
    #successful form means you save user record in database and redirect them to the database

def adminaccount(request):
    return render(request, "adminaccount.html")

def log_out(request):
    logout(request)
    return redirect("home")

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            form.authenticate_email()
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})

@login_required
def account(request):
    # Right now this only accomodates for student accounts!
    return render(request, "account.html", {"student": request.user.student})

@login_required
def show_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        lessons = booking.lesson_set.all()
    except ObjectDoesNotExist:
        return redirect("bookings_list")
    else:
        return render(request, "show_booking.html", {"lessons": lessons})


@login_required
def bookings_list(request):
    if request.user.is_student is False:
        return redirect("account")
    bookings = request.user.student.booking_set.all()
    return render(request, "bookings_list.html", {"bookings": bookings})


@login_required
def requests_list(request):
    if request.user.is_student is False:
        return redirect("home")
    requests = request.user.student.requestforlessons_set.all()
    return render(request, "requests_list.html", {"requests": requests})


@login_required
def show_request(request, lessons_request_id):
    # https://github.com/testdrivenio/django-ajax-xhr
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        booking = get_object_or_404(RequestForLessons, id=lessons_request_id)
        if request.method == "DELETE":
            booking.delete()
            return JsonResponse({"status": "Booking deleted!"})
        return JsonResponse({"status": "Invalid request"}, status=400)
    else:
        # todo: display the request
        pass


@login_required
def create_request(request):
    if request.method == "POST":
        form = RequestForLessonsForm(request.POST, student=request.user.student)
        if form.is_valid():
            form.save()
            return redirect("requests_list")

    else:
        form = RequestForLessonsForm(student=request.user.student)
    return render(request, "create_request.html", {"form": form})

def payment(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = PaymentForm(request.POST)
            if form.is_valid():
                try:
                    invoice = Invoice.objects.get(urn=form.cleaned_data.get("invoice_urn"))
                    invoice.is_paid = True
                    invoice.save()
                except ObjectDoesNotExist:
                    form = PaymentForm()
                    return render(request, "payment_form.html", {"form": form})
                return redirect("account")
        else:
            return redirect('log_in')
    else:
        form = PaymentForm(request.POST)
    return render(request, "payment_form.html", {"form": form})
