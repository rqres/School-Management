from django import forms
from .models import Student

class SignUpForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'school_name']

    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    password_confirm = forms.CharField(label='Re-enter password', widget=forms.PasswordInput())
    
class LogInForm(forms.Form):
    email = forms.CharField(label = "Email")
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
