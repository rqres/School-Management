from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect
from .forms import (
    RequestForLessonsForm,
    SchoolTermForm,
    StudentSignUpForm,
    SelectChildForm,
    PaymentForm,
    LogInForm,
    ForgotPasswordForm,
    RegisterChildForm,
    FulfillLessonRequestForm,
)
from .models import Booking, Invoice, RequestForLessons, SchoolTerm, User


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
# def sign_up_admin(request):
#     if request.method == "POST":
#         form = SignUpAdminForm(
#             request.POST
#         )  # creates a bound version of the form with post data
#         if form.is_valid():
#             form.save()
#             return redirect("account")
#     else:
#         form = (
#             SignUpAdminForm()
#         )  # create a form with SignUpAdminForm constructor, pass that form to template to render it
#     return render(request, "sign_up_admin.html", {"form": form})
#     # successful form means you save user record in database and redirect them to the database


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
        # print("Who are you ?? " + str(request.user))
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
        if request.user.is_school_admin:
            return redirect("all_requests_list")
        else:
            return redirect("requests_list")

    else:
        return render(request, "show_request.html", {"lessons_request": req})


@login_required
def delete_request(request, id):
    req = get_object_or_404(RequestForLessons, id=id)
    if req:
        req.delete()
        print("success!")

    if request.user.is_school_admin:
        return redirect("all_requests_list")
    else:
        return redirect("requests_list")


def fulfill_request(request, id):
    lesson_request = RequestForLessons.objects.get(id=id)

    if request.method == "POST":
        form = FulfillLessonRequestForm(request.POST, lesson_request=lesson_request)
        if form.is_valid():
            booking = form.save()
            print(booking)
            return redirect("all_requests_list")
    else:
        form = FulfillLessonRequestForm(lesson_request=lesson_request)

    student_name = (
        lesson_request.student.user.first_name
        + " "
        + lesson_request.student.user.last_name
    )

    return render(
        request,
        "fulfill_request_form.html",
        {"request_id": id, "form": form, "student_name": student_name},
    )


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


@login_required
def all_requests_list(request):
    if not request.user.is_school_admin:
        return redirect("account")

    all_requests = RequestForLessons.objects.all()
    return render(request, "all_requests_list.html", {"all_requests": all_requests})


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


def register_child(request):
    if request.user.is_parent:
        if request.method == "POST":
            form = RegisterChildForm(request.POST)
            if form.is_valid():
                form.authenticate(request.user)
                return render(
                    request,
                    "register_child.html",
                    {
                        "form": form,
                        "parent": request.user,
                        "children": request.user.children.all(),
                    },
                )
            else:
                return redirect("account")
        else:
            form = RegisterChildForm()
            return render(
                request,
                "register_child.html",
                {
                    "form": form,
                    "parent": request.user,
                    "children": request.user.children.all(),
                },
            )
    else:
        return redirect("account")


@login_required
def select_child(request):
    if request.method == "POST":
        form = SelectChildForm(request.POST)
        form.set_children(request.user.children.all())
        if form.is_valid():
            selected_child_email = form.cleaned_data["child_box"]
            child = User.objects.get(email__exact=selected_child_email)
            child_requests = child.student.requestforlessons_set.all()
            child_bookings = child.student.booking_set.all()

            request_child_form = RequestForLessonsForm(
                request.POST, student=child.student
            )
            if request_child_form.is_valid():
                request_child_form.save()

            return render(
                request,
                "select_child.html",
                {
                    "form": form,
                    "email": selected_child_email,
                    "bookings": child_bookings,
                    "requests": child_requests,
                    "child_form": request_child_form,
                },
            )
    else:
        form = SelectChildForm()
        form.set_children(request.user.children.all())
    return render(request, "select_child.html", {"form": form, "email": ""})


@login_required
def school_terms_list(request):
    if not request.user.is_school_admin:
        return redirect("account")
    school_terms = SchoolTerm.objects.all()
    return render(request, "school_terms_list.html", {"school_terms": school_terms})


@login_required
# TODO:  @adminrequired
def create_school_term(request):
    if not request.user.is_school_admin:
        return redirect("account")

    if request.method == "POST":
        form = SchoolTermForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("school_terms_list")

    else:
        form = SchoolTermForm()
    return render(request, "create_school_term.html", {"form": form})

@login_required
def delete_school_term(request, school_term_id):
    term = SchoolTerm.objects.get(id=school_term_id)
    if term:
        term.delete()
        print(f"Request {school_term_id} deleted")
        return redirect("school_terms_list")
    print("cant find term")

@login_required
def edit_school_term(request, id):
    if not request.user.is_school_admin:
        return redirect("account")

    term = get_object_or_404(SchoolTerm, id=id)

    if request.method == "POST":
        form = SchoolTermForm(request.POST, instance=term)

        # form.is_valid() will call term.clean()
        # the term needs to be hidden right before being cleaned
        # so as not to check overlapping against itself
        term._editing = True
        term.save()
        if form.is_valid():
            # finished editing
            term._editing = False
            term.save()

            term = form.save(edit=True)
            term.save()
            return redirect("school_terms_list")

    else:
        form = SchoolTermForm(instance=term)
    return render(
        request, "edit_school_term.html", {"school_term_id": id, "form": form}
    )