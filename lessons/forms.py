from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Student, User


class StudentSignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "school_name"]

    # password = forms.CharField(label="Password",widget=forms.PasswordInput())
    # password_confirm = forms.CharField(
    #     label="Re-enter password", widget=forms.PasswordInput()
    # )

    @transaction.atomic
    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get("email"),
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
            # password=self.cleaned_data.get("new_password"),
        )
        user.is_student = True

        user.save()
        student = Student.objects.create(user=user)
        student.school_name = self.cleaned_data.get("school_name")
        return user
