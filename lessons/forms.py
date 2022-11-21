from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import RequestForLessons, Student, User


class StudentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "school_name"]

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    # password = forms.CharField(label="Password",widget=forms.PasswordInput())
    # password_confirm = forms.CharField(
    #     label="Re-enter password", widget=forms.PasswordInput()
    # )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        # super().save(commit=False)
        # user = User.objects.create_user(
        #     self.cleaned_data.get("email"),
        #     first_name=self.cleaned_data.get("first_name"),
        #     last_name=self.cleaned_data.get("last_name"),
        #     password=self.cleaned_data.get("password"),
        # )
        # # password = forms.CharField(label='Password', widget=forms.PasswordInput())
        # # password_confirm = forms.CharField(label='Re-enter password', widget=forms.PasswordInput())
        # user.is_student = True

        # user.save()
        # Save the provided password in hashed format
        user = super(StudentSignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
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
        self._usr = kwargs.pop("usr", None)
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
            student=self._usr,
            no_of_lessons=self.cleaned_data.get("no_of_lessons"),
            days_between_lessons=self.cleaned_data.get("days_between_lessons"),
            lesson_duration=self.cleaned_data.get("lesson_duration"),
            other_info=self.cleaned_data.get("other_info"),
        )

        return req
