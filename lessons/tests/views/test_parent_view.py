from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student
from lessons.tests.helpers import LogInTester

# Create your tests here.
class LogInTest(TestCase, LogInTester):
    def setUp(self):
        self.sample_email = "parent@parents.com"
        self.user = User.objects.create_user(
            email=self.sample_email,
            first_name="A",
            last_name="Parent",
            password="password",
        )
        self.user.is_parent = True
        self.user.save()
    
    def test_parent_form_login(self):
        valid_pass = (self.sample_email, "password")
        self.assertTrue(
            self.client.login(username=valid_pass[0], password=valid_pass[1])
        )
        self.assertTrue(self.is_logged_in())
        self.assertTrue(self.user.is_parent)
    
    def test_parent_register_child(self):
        register_child_page = reverse('register_child')
        self.assertEqual(register_child_page, '/account/register_child/')
        # response = self.client.get(register_child_page, follow=True, data=self.user.is_parent)
        
