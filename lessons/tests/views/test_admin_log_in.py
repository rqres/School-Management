from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import LogInTester


# Create your tests here.
class LogInTest(TestCase, LogInTester):
    def setUp(self):
        self.sample_email = "admin@important.com"
        self.url = reverse("log_in")
        self.user = User.objects.create_superuser(
            email=self.sample_email,
            first_name="Keroen",
            last_name="Jeppens",
            password="password",
        )
        self.user.save()

    def test_admin_log_in_and_redirect(self):
        valid_pass = (self.sample_email, "password")
        self.assertTrue(
            self.client.login(username=valid_pass[0], password=valid_pass[1])
        )
        self.assertTrue(self.is_logged_in())

        admin_page = reverse("account")
        self.assertEqual(admin_page, "/account/")

    #   response = self.client.get(admin_page, follow=True)
    #   self.assertRedirects(response, admin_page, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    # """Unit tests of the log in form."""
    # from django.test import TestCase
    # from django import forms
    # from lessons.forms import LogInForm
    #
    # class AdminLogInFormTestCase(TestCase):
    #     """Unit tests of the log in form."""
    #
    #     def setUp(self):
    #         self.form_input = {'email':'marty.major@example.org', 'password':'Password123'}
    #
    #     #check if login page includes username and password field
    #     def test_form_contains_required_fields(self):
    #         form = LogInForm()
    #         self.assertIn('email', form.fields)
    #         self.assertIn('password', form.fields)
    #         #needs to use password input widget rather than regular text field
    #         password_field = form.fields['password']
    #         self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))
    #
    #     def test_form_accepts_valid_input(self):
    #         form = LogInForm(data=self.form_input)
    #         self.assertTrue(form.is_valid())
    #
    #     def test_form_rejects_blank_username(self):
    #         self.form_input['email'] = ''
    #         form = LogInForm(data=self.form_input)
    #         self.assertFalse(form.is_valid())
    #
    #     def test_form_rejects_blank_password(self):
    #         self.form_input['password'] =''
    #         form = LogInForm(data=self.form_input)
    #         self.assertFalse(form.is_valid())
    #
    #     #accepts incorrect username but just won't let them log in
    #     def test_form_accepts_incorrect_username(self):
    #         self.form_input['email'] = 'jane.d@example.org'
    #         form = LogInForm(data=self.form_input)
    #         self.assertTrue(form.is_valid())
    #
    #     #accepts incorrect password but just won't let them log in
    #     def test_form_accepts_incorrect_password(self):
    #         self.form_input['password'] = 'pwd'
    #         form = LogInForm(data=self.form_input)
    #         self.assertTrue(form.is_valid())
