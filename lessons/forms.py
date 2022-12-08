from copy import Error
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import (
    Lesson,
    Booking,
    Invoice,
    RequestForLessons,
    SchoolTerm,
    Teacher,
    Student,
    User,
    SchoolAdmin,
)
from django.contrib.auth import authenticate


class StudentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "school_name"]

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$",
                message="Password must contain at least one uppercase"
                "character, one lowercase character, and one digit.",
            )
        ],
    )

    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(StudentSignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.is_student = True
            user.save()

        Student.objects.create(
            user=user, school_name=self.cleaned_data.get("school_name")
        )

        return user
    
class ParentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "school_name"]

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$",
                message="Password must contain at least one uppercase"
                "character, one lowercase character, and one digit.",
            )
        ],
    )

    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ParentSignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.is_student = True
            user.is_parent = True
            user.save()

        Student.objects.create(
            user=user, school_name=self.cleaned_data.get("school_name")
        )

        return user


class EditAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)

        if self._instance:
            self.fields["first_name"].initial = self._instance.user.first_name
            self.fields["last_name"].initial = self._instance.user.last_name
            self.fields["school_name"].initial = self._instance.school_name
            self.fields["is_director"].initial = self._instance.is_director
            self.fields["can_edit_admins"].initial = self._instance.can_edit_admins
            self.fields["can_delete_admins"].initial = self._instance.can_delete_admins
            self.fields["can_create_admins"].initial = self._instance.can_create_admins

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "school_name",
            "is_director",
            "can_create_admins",
            "can_edit_admins",
            "can_delete_admins",
        ]

    school_name = forms.CharField(max_length=100)
    is_director = forms.BooleanField(label="Director?", required=False)
    can_create_admins = forms.BooleanField(
        label="Allow them to create admins?", required=False
    )
    can_edit_admins = forms.BooleanField(
        label="Allow them to edit admins?", required=False
    )
    can_delete_admins = forms.BooleanField(
        label="Allow them to delete admins?", required=False
    )

    def save(self):
        super().save(commit=False)
        admin = self._instance
        admin.user.first_name = self.cleaned_data.get("first_name")
        admin.user.last_name = self.cleaned_data.get("last_name")
        admin.school_name = self.cleaned_data.get("school_name")
        admin.is_director = self.cleaned_data.get("is_director")
        admin.can_edit_admins = self.cleaned_data.get("can_edit_admins")
        admin.can_delete_admins = self.cleaned_data.get("can_delete_admins")
        admin.can_create_admins = self.cleaned_data.get("can_create_admins")
        admin.user.save()
        admin.save()

        return admin


class CreateAdminForm(UserCreationForm):
    school_name = forms.CharField(max_length=100)
    is_director = forms.BooleanField(label="Director?", required=False)
    can_create_admins = forms.BooleanField(
        label="Allow them to create admins?", required=False
    )
    can_edit_admins = forms.BooleanField(
        label="Allow them to edit admins?", required=False
    )
    can_delete_admins = forms.BooleanField(
        label="Allow them to delete admins?", required=False
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "school_name",
            "is_director",
            "can_create_admins",
            "can_edit_admins",
            "can_delete_admins",
            "password1",
            "password2",
        ]

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$",
                message="Password must contain at least one uppercase"
                "character, one lowercase character, and one digit.",
            )
        ],
    )
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CreateAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.is_school_admin = True
            user.save()
        admin = SchoolAdmin.objects.create(
            user=user,
            school_name=self.cleaned_data.get("school_name"),
            is_director=self.cleaned_data.get("is_director"),
            can_create_admins=self.cleaned_data.get("can_create_admins"),
            can_edit_admins=self.cleaned_data.get("can_edit_admins"),
            can_delete_admins=self.cleaned_data.get("can_delete_admins"),
        )

        #if director is true, set all privileges to true and then .save again
        if admin.is_director:
            admin.can_create_admins = True
            admin.can_edit_admins = True
            admin.can_delete_admins = True

        admin.save()
        return admin


class LogInForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class SchoolTermForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)

        # this if statement is executed if the user is using the form to
        # update an existing school term
        # this block populates the fields with the existing data in the model
        if self._instance:
            self.fields["start_date"].initial = self._instance.start_date
            self.fields["end_date"].initial = self._instance.end_date

    class Meta:
        model = SchoolTerm
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, edit=False):
        super().save(commit=False)
        if not edit:
            school_term = SchoolTerm.objects.create(
                start_date=self.cleaned_data.get("start_date"),
                end_date=self.cleaned_data.get("end_date"),
            )
        else:
            # if the user is editing a school term, don't create a new object
            # but instead update its fields
            school_term = self._instance
            school_term.start_date = self.cleaned_data.get("start_date")
            school_term.end_date = self.cleaned_data.get("end_date")

        return school_term


class RequestForLessonsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop("user", None)
        self._instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)

        # this if statement is executed if the user is using the form to
        # update an existing request
        # this block populates the fields with the existing data in the model
        if self._instance:
            avlb_list = self._instance.availability.split(",")
            self.fields["no_of_lessons"].initial = self._instance.no_of_lessons
            self.fields[
                "days_between_lessons"
            ].initial = self._instance.days_between_lessons
            self.fields["lesson_duration"].initial = self._instance.lesson_duration
            self.fields["availability_field"].initial = avlb_list
            self.fields["other_info"].initial = self._instance.other_info

    class Meta:
        model = RequestForLessons
        fields = [
            "no_of_lessons",
            "days_between_lessons",
            "lesson_duration",
            "other_info",
            "availability_field",
        ]
        widgets = {
            "other_info": forms.Textarea(),
        }

    WEEKDAYS = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    availability_field = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        label="Which days are you available?",
        widget=forms.CheckboxSelectMultiple,
    )

    def save(self, edit=False):
        super().save(commit=False)
        if not edit:
            req = RequestForLessons.objects.create(
                user=self._user,
                availability=",".join(self.cleaned_data.get("availability_field")),
                no_of_lessons=self.cleaned_data.get("no_of_lessons"),
                days_between_lessons=self.cleaned_data.get("days_between_lessons"),
                lesson_duration=self.cleaned_data.get("lesson_duration"),
                other_info=self.cleaned_data.get("other_info"),
            )
        else:
            # if the user is editing a request, don't create a new object
            # but instead update its fields
            req = self._instance
            req.availability = ",".join(self.cleaned_data.get("availability_field"))
            req.no_of_lessons = self.cleaned_data.get("no_of_lessons")
            req.days_between_lessons = self.cleaned_data.get("days_between_lessons")
            req.lesson_duration = self.cleaned_data.get("lesson_duration")
            req.other_info = self.cleaned_data.get("other_info")
            req.save()

        return req


class EditBookingForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        label="Select teacher", queryset=Teacher.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self._booking = kwargs.pop("booking", None)
        super().__init__(*args, **kwargs)

        if self._booking:
            self.fields["teacher"].initial = self._booking.teacher
            self.fields["num_of_lessons"].initial = self._booking.num_of_lessons
            self.fields[
                "days_between_lessons"
            ].initial = self._booking.days_between_lessons
            self.fields["lesson_duration"].initial = self._booking.lesson_duration
            self.fields["description"].initial = self._booking.description

    class Meta:
        model = Booking
        fields = [
            "num_of_lessons",
            "days_between_lessons",
            "lesson_duration",
            "teacher",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(),
        }

    def save(self):
        super().save(commit=False)
        self._booking.num_of_lessons = self.cleaned_data.get("num_of_lessons")
        self._booking.days_between_lessons = self.cleaned_data.get(
            "days_between_lessons"
        )
        self._booking.lesson_duration = self.cleaned_data.get("lesson_duration")
        self._booking.teacher = self.cleaned_data.get("teacher")
        self._booking.description = self.cleaned_data.get("description")
        self._booking.save()
        self._booking.update_lessons()
        self._booking.update_invoice()
        return self._booking


class EditLessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._lesson = kwargs.pop("lesson", None)
        super().__init__(*args, **kwargs)

        if self._lesson:
            self.fields["name"].initial = self._lesson.name
            self.fields["date"].initial = self._lesson.date
            self.fields["startTime"].initial = self._lesson.startTime
            self.fields["description"].initial = self._lesson.description

    class Meta:
        model = Lesson
        fields = ["name", "date", "startTime", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "startTime": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(),
        }

    def save(self):
        super().save(commit=False)
        self._lesson.name = self.cleaned_data.get("name")
        self._lesson.date = self.cleaned_data.get("date")
        self._lesson.startTime = self.cleaned_data.get("startTime")
        self._lesson.description = self.cleaned_data.get("description")
        self._lesson.save()

        return self._lesson


class PaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self._user:
            invoices = self._user.invoice_set.filter(is_paid=False)
            self.fields["invoice_urn"].queryset = invoices

    invoice_urn = forms.ModelChoiceField(
        label="Invoice reference number", queryset=Invoice.objects.all()
    )
    account_name = forms.CharField(max_length=50)
    account_number = forms.CharField(
        min_length=8,
        max_length=8,
        validators=[
            RegexValidator(
                regex=r"^[0-9]*$", message="Account number must contain numbers only"
            )
        ],
    )
    sort_code = forms.CharField(
        min_length=6,
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^[0-9]*$", message="Sort code must contain numbers only"
            )
        ],
    )
    postcode = forms.CharField(
        label="Postcode",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$",
                # Provide by wikipedia page https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Validation
                message="Postcode must be valid",
            )
        ],
    )

    def clean_invoice(self):
        invoice_urn = self.cleaned_data.get("invoice_urn")
        if not Invoice.objects.filter(urn=invoice_urn).exists():
            raise forms.ValidationError("Enter valid invoice urn")


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    message = ""

    def authenticate_email(self):
        checked_email = self.cleaned_data.get("email")
        if User.objects.filter(email=checked_email).exists():
            self.message = (
                "Instructions for password reset sent to your e-mail address."
            )
        else:
            self.message = "This e-mail address is not registered to any account."


class RegisterChildForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = password = forms.CharField(
        label="Password", widget=forms.PasswordInput()
    )
    message = ""

    def authenticate(self, parent):
        checked_email = self.cleaned_data.get("email")
        checked_pass = self.cleaned_data.get("password")
        child = authenticate(username=checked_email, password=checked_pass)
        if child == parent:
            self.message = "You cannot add yourself as your own child."
        elif parent.children.filter(email=checked_email).exists():
            self.message = "This user is already registered as your own child."
        elif child is not None:
            self.message = (
                "This user, "
                + child.first_name
                + " "
                + child.last_name
                + " has been registered as your child."
            )
            parent.children.add(child)
            child.parents.add(parent)
        else:
            self.message = "Incorrect e-mail or password specified."


class SelectChildForm(forms.ModelForm):
    child_list = []
    child_box = forms.ModelChoiceField(
        label="Select child", queryset=User.objects.all()
    )

    class Meta:
        model = User
        fields = []

    def set_children(self, children):
        self.child_list.clear()
        for child in children:
            self.child_list.append(child.email)
        self.fields["child_box"].queryset = User.objects.filter(
            email__in=self.child_list
        )


class FulfillLessonRequestForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        label="Select teacher", queryset=Teacher.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self._lesson_request = kwargs.pop("lesson_request", None)
        super().__init__(*args, **kwargs)

        self.fields["num_of_lessons"].initial = self._lesson_request.no_of_lessons
        self.fields[
            "days_between_lessons"
        ].initial = self._lesson_request.days_between_lessons
        self.fields["lesson_duration"].initial = self._lesson_request.lesson_duration

    class Meta:
        model = Booking
        fields = [
            # student should not be a field in this
            "teacher",
            "num_of_lessons",
            "days_between_lessons",
            "lesson_duration",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(),
        }

    # transaction atomic means that if anything fails in this function
    # then everything will revert to the state it was in before running the function
    # aka all operations in this function are part of one single (atomic) operation
    # this is useful because we do not want e.g to mark the request as fulfilled
    # in case creating the booking fails
    @transaction.atomic
    def save(self):
        super().save(commit=False)

        booking = Booking.objects.create(
            num_of_lessons=self.cleaned_data.get("num_of_lessons"),
            days_between_lessons=self.cleaned_data.get("days_between_lessons"),
            lesson_duration=self.cleaned_data.get("lesson_duration"),
            description=self.cleaned_data.get("description"),
            user=self._lesson_request.user,
            teacher=self.cleaned_data.get("teacher"),
        )
        try:
            booking.create_lessons()
        except AttributeError:
            raise Exception("No School Term in DB")

        # booking created, mark request as fulfilled
        self._lesson_request.fulfilled = True
        self._lesson_request.save()

        return booking
