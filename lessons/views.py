from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect
from .forms import (
    RequestForLessonsForm,
    SchoolTermForm,
    StudentSignUpForm,
    PaymentForm,
    LogInForm,
    ForgotPasswordForm,
    SignUpAdminForm,
)
from .models import Booking, Invoice, RequestForLessons, SchoolTerm


#  Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("account")

    return render(request, "home.html")


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
    else:
        form = LogInForm()
    return render(request, "log_in.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect("home")


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            form.authenticate_email()
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})


def sign_up(request):
    return render(request, "sign_up.html")


def sign_up_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            # create user, add it to db, and log them in
            user = form.save()
            login(request, user)
            return redirect("account")
    else:
        form = StudentSignUpForm()

    return render(request, "sign_up_student.html", {"form": form})


# check if the user is a director then display sign up page
def sign_up_admin(request):
    if request.method == "POST":
        form = SignUpAdminForm(
            request.POST
        )  # creates a bound version of the form with post data
        if form.is_valid():
            form.save()
            return redirect("account")
    else:
        form = (
            SignUpAdminForm()
        )  # create a form with SignUpAdminForm constructor, pass that form to template to render it
    return render(request, "sign_up_admin.html", {"form": form})
    # successful form means you save user record in database and redirect them to the database


@login_required
def account(request):
    # redirect school admins to their dashboard template
    if request.user.is_school_admin:
        return render(
            request, "account_admin.html", {"school_admin": request.user.schooladmin}
        )
    # redirect students to student template
    elif request.user.is_student:
        return render(
            request, "account_student.html", {"student": request.user.student}
        )
    # redirect sys admins to Django admin page
    elif request.user.is_admin:
        return redirect("admin:index")
    # elif request.user.is_parent:
    #   etc...
    else:
        # UNRECOGNIZED USER TYPE
        # this shouldn't happen, log user out and send him to welcome page
        print("Who are you ?? " + str(request.user))
        logout(request)
        return redirect("home")


@login_required
def bookings_list(request):
    if request.user.is_student is False:
        return redirect("account")
    bookings = request.user.student.booking_set.all()
    return render(request, "bookings_list.html", {"bookings": bookings})


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
def requests_list(request):
    if request.user.is_student is False:
        return redirect("home")
    requests = request.user.student.requestforlessons_set.all()
    return render(request, "requests_list.html", {"requests": requests})


@login_required
def show_request(request, id):
    try:
        req = RequestForLessons.objects.get(id=id)
    except ObjectDoesNotExist:
        return redirect("requests_list")
    else:
        return render(request, "show_request.html", {"lessons_request": req})


@login_required
def delete_request(request, id):
    req = get_object_or_404(RequestForLessons, id=id)
    if req:
        req.delete()
        print("success!")

    return redirect("requests_list")


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


@login_required
def edit_request(request, id):
    req = get_object_or_404(RequestForLessons, id=id)

    if request.method == "POST":
        form = RequestForLessonsForm(
            request.POST, instance=req, student=request.user.student
        )
        if form.is_valid():
            req = form.save(edit=True)
            req.save()
            return redirect("requests_list")

    else:
        form = RequestForLessonsForm(instance=req)
    return render(request, "edit_request.html", {"request_id": id, "form": form})


def payment(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = PaymentForm(request.POST)
            if form.is_valid():
                try:
                    invoice = Invoice.objects.get(
                        urn=form.cleaned_data.get("invoice_urn")
                    )
                    invoice.is_paid = True
                    invoice.save()
                except ObjectDoesNotExist:
                    form = PaymentForm()
                    return render(request, "payment_form.html", {"form": form})
                return redirect("account")
        else:
            return redirect("log_in")
    else:
        form = PaymentForm(request.POST)
    return render(request, "payment_form.html", {"form": form})


def school_terms_list(request):
    if not request.user.is_school_admin:
        return redirect("account")
    school_terms = SchoolTerm.objects.all()
    return render(request, "school_terms_list.html", {"school_terms": school_terms})


def create_school_term(request):
    if request.method == "POST":
        form = SchoolTermForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("school_terms_list")

    else:
        form = SchoolTermForm()
    return render(request, "create_school_term.html", {"form": form})
