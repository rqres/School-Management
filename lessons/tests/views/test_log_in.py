from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student, SchoolAdmin
from lessons.tests.helpers import LogInTester
from lessons.forms import LogInForm

# Create your tests here.
class LogInTest(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse("log_in")
        self.user = User.objects.create_user(
            email="student@example.org",
            first_name="Real",
            last_name="Person",
            password="Password123",
            is_active=True,
        )
        self.user.save()

    def test_url(self):
        self.assertEqual(self.url, "/log_in/")

    #check if ther form is being displayed correctly
    def test_get_log_in(self):
        response = self.client.get(self.url) #use that to make requests and simulate responses programatically
        #status code should be 200 from responses
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    def test_failed_login_pass(self):
        invalid_pass = ("user@example.org", "passwor")
        self.assertFalse(
            self.client.login(email=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_failed_login_email(self):
        invalid_pass = ("notAnEmail", "password")
        self.assertFalse(
            self.client.login(email=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_unsuccessful_log_in(self):
        form_input = {'email':'user@example.org', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.is_logged_in())

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active=False
        self.user.save()
        form_input = {'email': 'user@example.org', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.is_logged_in())

    def test_log_in_with_blank_email(self):
        form_input = {'email':'', 'password': 'Password123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(self.is_logged_in())

    def test_log_in_with_blank_password(self):
        form_input = {'email': 'example.email@fox.org', 'password' : ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(self.is_logged_in())
