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

        admin_page = reverse("account_admin")
        self.assertEqual(admin_page, "/adminaccount/")

    #   response = self.client.get(admin_page, follow=True)
    #   self.assertRedirects(response, admin_page, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
