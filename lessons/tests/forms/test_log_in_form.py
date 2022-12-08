"""Unit tests of the log in form."""
from django.test import TestCase
from django import forms
from lessons.forms import LogInForm

class LogInFormTestCase(TestCase):
    """Unit tests of the log in form."""

    def setUp(self):
        self.form_input = {'email':'user@example.org', 'password':'Password123'}

    #check if login page includes username and password field
    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        #needs to use password input widget rather than regular text field
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))

    def test_form_accepts_valid_input(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_username(self):
        self.form_input['email'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] =''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    #accepts incorrect username but just won't let them log in
    def test_form_accepts_incorrect_username(self):
        self.form_input['email'] = 'userexample'
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    #accepts incorrect password but just won't let them log in
    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'passwprd'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())
