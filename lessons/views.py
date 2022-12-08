from django.contrib.admin.options import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect
from .models import (
    Booking,
    Invoice,
    RequestForLessons,
    SchoolTerm,
    SchoolAdmin,
    User,
    Lesson,
)
from .forms import (
    EditAdminForm,
    RequestForLessonsForm,
    SchoolTermForm,
    StudentSignUpForm,
    ParentSignUpForm,
    SelectChildForm,
    PaymentForm,
    LogInForm,
    ForgotPasswordForm,
    RegisterChildForm,
    FulfillLessonRequestForm,
    EditBookingForm,
    EditLessonForm,
    CreateAdminForm,
)


#  Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("account")

    return render(request, "home.html")


def log_in(request):
    if request.user.is_authenticated:
        return redirect("account")

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
    if request.user.is_authenticated:
        return redirect("account")

    return render(request, "sign_up.html")


def sign_up_student(request):
    if request.user.is_authenticated:
        return redirect("account")

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


def sign_up_parent(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        form = ParentSignUpForm(request.POST)
        if form.is_valid():
            # create user, add it to db, and log them in
            user = form.save()
            login(request, user)
            return redirect("account")
    else:
        form = ParentSignUpForm()
    return render(request, "sign_up_parent.html", {"form": form})

def create_admin(request):
    if request.method == "POST":
        # create a bound version of the form with post data
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_list")
    else:
        form = (
            CreateAdminForm()
        )  # create a form with CreateAdminForm constructor, pass that form to template to render it
    return render(request, "create_admin.html", {"form": form})
    # successful form means you save user record in database and redirect them to the database


@login_required
def account(request):
    # redirect school admins to their dashboard template
    if request.user.is_school_admin and request.user.is_active:
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
        logout(request)
        return redirect("account")


@login_required
def bookings_list(request):
    if request.user.is_school_admin is True:
        try:
            bookings = Booking.objects.all()
        except ObjectDoesNotExist:
            return redirect("bookings_list")
    else:
        bookings = request.user.booking_set.all()
    return render(
        request, "bookings_list.html", {"bookings": bookings, "user": request.user}
    )


@login_required
def show_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        lessons = booking.lesson_set.all()
        if request.user.is_school_admin is False and booking.user != request.user:
            # Users can only their bookings
            return redirect("account")
    except ObjectDoesNotExist:
        return redirect("bookings_list")
    else:
        return render(
            request, "show_booking.html", {"lessons": lessons, "user": request.user}
        )


@login_required
def edit_lesson(request, booking_id, lesson_id):
    if request.user.is_school_admin is False:
        return redirect("account")
    try:
        booking = Booking.objects.get(id=booking_id)
        lesson = Lesson.objects.get(id=lesson_id)
        if request.method == "POST":
            form = EditLessonForm(request.POST, lesson=lesson)
            if form.is_valid():
                lesson = form.save()
                return redirect("show_booking", booking_id=booking.id)
            else:
                form = EditLessonForm(lesson=lesson)
    except ObjectDoesNotExist:
        return redirect("show_booking", booking_id=booking.id)
    else:
        form = EditLessonForm(lesson=lesson)
        return render(
            request,
            "edit_lesson.html",
            {"lesson": lesson, "booking": booking, "form": form},
        )


@login_required  # needs to be admin login
def delete_booking(request, booking_id):
    if request.user.is_school_admin is False:
        return redirect("account")
    try:
        booking = Booking.objects.get(id=booking_id)
        booking_name = str(booking)
        booking.delete()
    except ObjectDoesNotExist:
        return redirect("bookings_list")
    else:
        return render(request, "delete_booking.html", {"booking_name": booking_name})


@login_required  # needs to be admin login
def edit_booking(request, booking_id):
    if request.user.is_school_admin is False:
        return redirect("account")
    try:
        booking = Booking.objects.get(id=booking_id)
        if request.method == "POST":
            form = EditBookingForm(request.POST, booking=booking)
            if form.is_valid():
                booking = form.save()
                return redirect("bookings_list")
            else:
                form = EditBookingForm(booking=booking)
    except ObjectDoesNotExist:
        return redirect("bookings_list")
    else:
        form = EditBookingForm(booking=booking)
        return render(request, "edit_booking.html", {"booking": booking, "form": form})


@login_required
def requests_list(request):
    if request.user.is_school_admin:
        requests = RequestForLessons.objects.all()
    else:
        requests = request.user.requestforlessons_set.all()

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


def fulfill_request(request, id):
    if not request.user.is_school_admin:
        raise PermissionDenied

    lesson_request = RequestForLessons.objects.get(id=id)

    if request.method == "POST":
        form = FulfillLessonRequestForm(request.POST, lesson_request=lesson_request)
        if form.is_valid():
            booking = form.save()
            print(booking)
            return redirect("requests_list")
    else:
        form = FulfillLessonRequestForm(lesson_request=lesson_request)

    user_name = lesson_request.user.first_name + " " + lesson_request.user.last_name

    return render(
        request,
        "fulfill_request_form.html",
        {"request_id": id, "form": form, "user_name": user_name},
    )

def extract_email(string):
    email = ""
    i = len(string) - 1
    while (string[i] != " "):
        email += string[i]
        i -= 1
    return email[::-1]
        
@login_required
def create_request(request):
    if request.user.is_school_admin:
        raise PermissionDenied
    
    copy_of_request = request
    submitted_data = request.POST.get('submit_field')
    print(submitted_data)
    if submitted_data is not None:
        print(extract_email(submitted_data))
        request.user = User.objects.filter(email__exact = extract_email(submitted_data)).first()
        
    if request.method == "POST":
        form = RequestForLessonsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            if submitted_data is not None:
                return redirect("account")
            return redirect("requests_list")
    else:
        form = RequestForLessonsForm(user=request.user)
        
    if submitted_data is not None:
        return render(copy_of_request, "select_child.html", {"form": form, "email": extract_email(submitted_data)})
    return render(request, "create_request.html", {"form": form})


@login_required
def edit_request(request, id):
    if request.user.is_school_admin:
        raise PermissionDenied

    req = get_object_or_404(RequestForLessons, id=id)
    if request.method == "POST":
        form = RequestForLessonsForm(request.POST, instance=req, user=request.user)
        if form.is_valid():
            req = form.save(edit=True)
            req.save()
            return redirect("requests_list")
    else:
        form = RequestForLessonsForm(instance=req)
    return render(request, "edit_request.html", {"request_id": id, "form": form})


@login_required
def admin_list(request):
    if not request.user.is_school_admin:
        raise PermissionDenied

    admins = SchoolAdmin.objects.all().exclude(user=request.user)
    return render(
        request, "admin_list.html", {"admins": admins, "current_user": request.user}
    )

    # if request.user.schooladmin.is_director:
    #     return render(request, "admin_list.html", {"admins": admins})
    # elif request.user.schooladmin.editAdmins:
    #     return render(request, "admin_list_edit_only.html", {"admins": admins})
    # elif request.user.schooladmin.deleteAdmins:
    #     return render(request, "admin_list_delete_only.html", {"admins": admins})


@login_required
def edit_admin(request, id):
    if not (request.user.is_school_admin and request.user.schooladmin.is_director):
        raise PermissionDenied

    admin = get_object_or_404(SchoolAdmin, pk=id)

    if request.method == "POST":
        form = EditAdminForm(request.POST, instance=admin)
        if form.is_valid():
            admin = form.save()
            return redirect("admin_list")
    else:
        form = EditAdminForm(instance=admin)
    return render(request, "edit_admin.html", {"admin_id": id, "form": form})


@login_required
def delete_admin(request, id):
    if not (request.user.is_school_admin and request.user.schooladmin.is_director):
        raise PermissionDenied

    admin = get_object_or_404(SchoolAdmin, pk=id)
    if admin:
        admin.delete()
        print("success!")

    return redirect("admin_list")


@login_required
def payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                invoice = Invoice.objects.get(urn=form.cleaned_data.get("invoice_urn"))
                invoice.is_paid = True
                invoice.save()
                return redirect("account")
            except ObjectDoesNotExist:
                form = PaymentForm(user=request.user)
    else:
        form = PaymentForm(user=request.user)
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
    if request.user.is_parent:
        if request.method == "POST":
            form = SelectChildForm(request.POST)
            form.set_children(request.user.children.all())
            if form.is_valid():
                selected_child_email = form.cleaned_data["child_box"]
                child = User.objects.get(email__exact=selected_child_email)
                child_requests = child.requestforlessons_set.all()
                child_bookings = child.booking_set.all()

                request_child_form = RequestForLessonsForm(
                    request.POST, user=child
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
    else: 
        return redirect('account')

@login_required
def school_terms_list(request):
    if not request.user.is_school_admin:
        raise PermissionDenied

    school_terms = SchoolTerm.objects.all()
    return render(request, "school_terms_list.html", {"school_terms": school_terms})


@login_required
# TODO:  @adminrequired
def create_school_term(request):
    if not request.user.is_school_admin:
        raise PermissionDenied

    if request.method == "POST":
        form = SchoolTermForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("school_terms_list")

    else:
        form = SchoolTermForm()
    return render(request, "create_school_term.html", {"form": form})


@login_required
def delete_school_term(request, id):
    if not request.user.is_school_admin:
        raise PermissionDenied

    term = SchoolTerm.objects.get(id=id)
    if term:
        term.delete()
        print(f"SchoolTerm {id} deleted")

        return redirect("school_terms_list")
    print("cant find term")


@login_required
def edit_school_term(request, id):
    if not request.user.is_school_admin:
        raise PermissionDenied

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
