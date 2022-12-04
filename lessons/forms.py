from django import forms
from django.forms import Select
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Invoice, RequestForLessons, Student, User
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate


class StudentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100, required=True)
    is_parent = forms.BooleanField(label="Are you a Parent?", required=False)

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
            user.is_parent = self.cleaned_data["is_parent"]
            user.save()

        Student.objects.create(
            user=user, school_name=self.cleaned_data.get("school_name")
        )

        return user


class LogInForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class AdminLoginForm(forms.Form):
    adminemail = forms.EmailField(label="Email", required=True)
    adminpassword = forms.CharField(label="Password", widget=forms.PasswordInput())


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

    # availability_field = forms.MultipleChoiceField(
    #     choices=[("mon", "Monday"), ("tue", "Tuesday"), ("wed", "Wednesday")],
    #     label="Which days are you available?",
    #     widget=forms.CheckboxSelectMultiple(),
    # )

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
    password = password = forms.CharField(label="Password", widget=forms.PasswordInput())
    message = ""

    def authenticate(self, parent):
        checked_email = self.cleaned_data.get("email")
        checked_pass = self.cleaned_data.get("password")
        child = authenticate(username = checked_email, password = checked_pass)
        if child == parent:
            self.message = "You cannot add yourself as your own child."
        elif parent.children.filter(email = checked_email).exists():
            self.message = "This user is already registered as your own child."
        elif child is not None:
            self.message = ("This user, " + child.first_name + " " + child.last_name + 
                            " has been registered as your child.")
            parent.children.add(child)
            child.parents.add(parent)
        else:
            self.message = "Incorrect e-mail or password specified."

class SelectChildForm(forms.ModelForm):
    child_list = []
    child_box = forms.ModelChoiceField(label = "Select child", queryset = User.objects.all())

    class Meta:
        model = User
        fields = []
        
    def set_children(self, children):
        self.child_list.clear()
        for child in children:
            self.child_list.append(child.email)
        self.fields['child_box'].queryset = User.objects.filter(email__in = self.child_list)
        
        
    
    
        
    
