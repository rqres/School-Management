from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student
from lessons.tests.helpers import LogInTester


# Create your tests here.
class LogInTest(TestCase, LogInTester):
    def setUp(self):
        self.sample_email = "sample@text.com"
        self.url = reverse("log_in")
        user = User.objects.create_user(
            email=self.sample_email,
            first_name="Real",
            last_name="Person",
            password="password",
        )
        user.save()
        self.student = Student.objects.create(
            user=user, school_name="Queen's Trade School Waitangi"
        )

    def test_url(self):
        self.assertEqual(self.url, "/log_in/")

    def test_failed_login_pass(self):
        invalid_pass = (self.sample_email, "passwor")
        self.assertFalse(
            self.client.login(username=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_failed_login_email(self):
        invalid_pass = ("notAnEmail", "password")
        self.assertFalse(
            self.client.login(username=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_successful_login(self):
        valid_pass = (self.sample_email, "password")
        self.assertTrue(
            self.client.login(username=valid_pass[0], password=valid_pass[1])
        )
        self.assertTrue(self.is_logged_in())
