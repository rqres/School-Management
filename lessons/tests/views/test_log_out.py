from django.test import TestCase
from django.urls import reverse
from django.test import Client
from lessons.models import User, Student
from lessons.forms import LogInForm
from .helpers import LogInTester


# Create your tests here.
class LogOutTest(TestCase, LogInTester):
    def setUp(self):
        self.sample_email = "sample@text.com"
        self.url = reverse("log_out")
        self.user = User.objects.create_user(
            email=self.sample_email,
            first_name="Real",
            last_name="Person",
            password="password",
        )

    def test_url(self):
        self.assertEqual(self.url, "/log_out/")

    def test_log_in_and_outfailed_login_pass(self):
        self.client.login(username=self.sample_email, password="password")
        self.assertTrue(self.is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse("home")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "home.html")
        self.assertFalse(self.is_logged_in())
