from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import (
    Invoice,
    RequestForLessons,
    SchoolTerm,
    Student,
    User,
    SchoolAdmin
)


class StudentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100)

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


class SignUpAdminForm(UserCreationForm):
    school_name = forms.CharField(max_length=100)
    directorStatus = forms.BooleanField(label="Director?", required=False)
    createAdmins = forms.BooleanField(label="Create Admin privilege?", required=False)
    editAdmins = forms.BooleanField(label="Edit Admins privilege?", required=False)
    deleteAdmins = forms.BooleanField(label="Delete Admins privilege?", required=False)
    editTermDates = forms.BooleanField(label="Edit term dates privilege?", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "school_name", "directorStatus", "createAdmins", "editAdmins", "deleteAdmins"]
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
        user = super(SignUpAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.is_school_admin = True
            user.save()
        SchoolAdmin.objects.create(
            user=user,
            school_name=self.cleaned_data.get("school_name"),
            directorStatus=self.cleaned_data.get("directorStatus"),
            createAdmins=self.cleaned_data.get("createAdmins"),
            editAdmins=self.cleaned_data.get("editAdmins"),
            deleteAdmins=self.cleaned_data.get("deleteAdmins"),
            editTermDates=self.cleaned_data.get("editTermDates"),
        )

        return user


class LogInForm(forms.Form):
    email = forms.CharField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class SchoolTermForm(forms.ModelForm):
    class Meta:
        model = SchoolTerm
        fields = ["start_date", "end_date"]

    def save(self):
        super().save(commit=False)
        school_term = SchoolTerm.objects.create(
            start_date=self.cleaned_data.get("start_date"),
            end_date=self.cleaned_data.get("end_date"),
        )

        return school_term


class RequestForLessonsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = RequestForLessons
        fields = [
            "no_of_lessons",
            "days_between_lessons",
            "lesson_duration",
            "other_info",
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

    def save(self):
        super().save(commit=False)
        req = RequestForLessons.objects.create(
            student=self._student,
            availability=",".join(self.cleaned_data.get("availability_field")),
            no_of_lessons=self.cleaned_data.get("no_of_lessons"),
            days_between_lessons=self.cleaned_data.get("days_between_lessons"),
            lesson_duration=self.cleaned_data.get("lesson_duration"),
            other_info=self.cleaned_data.get("other_info"),
        )

        return req


class PaymentForm(forms.Form):
    invoice_urn = forms.CharField(label="Invoice reference number")
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
