from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Invoice, RequestForLessons, Student, User
from django.core.validators import RegexValidator

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


class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


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
        widgets = {"other_info": forms.Textarea()}

    def save(self):
        super().save(commit=False)
        req = RequestForLessons.objects.create(
            student=self._student,
            no_of_lessons=self.cleaned_data.get("no_of_lessons"),
            days_between_lessons=self.cleaned_data.get("days_between_lessons"),
            lesson_duration=self.cleaned_data.get("lesson_duration"),
            other_info=self.cleaned_data.get("other_info"),
        )

        return req

class PaymentForm(forms.Form):
    invoice_urn = forms.CharField(label="Invoice reference number")
    account_name =forms.CharField(max_length=50)
    account_number = forms.IntegerField(max_value=9999999) #change to char
    sort_code = forms.IntegerField(max_value=999999)
    postcode = forms.CharField(
        label="Postcode", 
        validators = [RegexValidator(
            regex=r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
            # Provide by wikipedia page https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Validation
            message='Postcode must be valid'
        )])