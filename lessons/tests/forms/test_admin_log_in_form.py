"""Unit tests of the log in form."""
from django.test import TestCase
from django import forms
from lessons.forms import AdminLoginForm

class AdminLogInFormTestCase(TestCase):
    """Unit tests of the log in form."""

    def setUp(self):
        self.form_input = {'username':'labdhi@example.org', 'password':'Password123'}

    #check if login page includes username and password field
    def test_form_contains_required_fields(self):
        form = AdminLoginForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
        #needs to use password input widget rather than regular text field
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))

    def test_form_accepts_valid_input(self):
        form = AdminLoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_username(self):
        self.form_input['username'] = ''
        form = AdminLoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] =''
        form = AdminLoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    #accepts incorrect username but just won't let them log in
    def test_form_accepts_incorrect_username(self):
        self.form_input['username'] = 'ja'
        form = AdminLoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    #accepts incorrect password but just won't let them log in
    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'pwd'
        form = AdminLoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())
