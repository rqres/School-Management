from django.test import TestCase
from django.urls import reverse
from django.test import Client
from lessons.models import User
from lessons.forms import LogInForm

# Create your tests here.
class LogInTest(TestCase):
    def setUp(self):
        self.sample_email = "sample@text.com"
        self.url = reverse('log_in')
        user = User.objects.create_user (
            username = self.sample_email,
            email = self.sample_email,
            password = "password",
            # first_name = "Real", 
            # last_name = "Person",
            # school_name = "Queen's Trade School Waitangi"
        )
        user.save()
    
    def test_url(self):
        self.assertEqual(self.url, '/log_in')
        
    def test_failed_login_pass(self):
        invalid_pass = (self.sample_email, "passwor")
        cli = Client()
        self.assertFalse(cli.login(username = invalid_pass[0], password = invalid_pass[1]))
    
    def test_failed_login_email(self):
        invalid_pass = ("notAnEmail", "password")
        cli = Client()
        self.assertFalse(cli.login(username = invalid_pass[0], password = invalid_pass[1]))
        
    def test_successful_login(self):
        valid_pass = (self.sample_email, "password")
        cli = Client()
        self.assertTrue(cli.login(username = valid_pass[0], password = valid_pass[1]))
