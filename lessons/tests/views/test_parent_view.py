from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student
from lessons.tests.helpers import LogInTester

# Create your tests here.
class LogInTest(TestCase, LogInTester):
    
    fixtures = [ 
                "lessons/tests/fixtures/default_parent.json",
                "lessons/tests/fixtures/other_users.json"  
                ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.parent = User.objects.get(email="par@ent.org")
        self.child = User.objects.get(email="other.user@example.org")
        self.child_form_details = {
            "email": self.child.email,
            "password": "Watermelon123"
        }
        self.reg_page = reverse('register_child')
        self.sel_page = reverse('select_child')
    
    def test_urls_correct(self):
        self.assertEqual(self.reg_page, '/account/register_child/')
        self.assertEqual(self.sel_page, '/account/select_child/')
        
    def test_parent_form_login(self):
        self.assertTrue(
            self.client.login(email=self.parent.email, password="Watermelon123")
        )
        self.assertTrue(self.is_logged_in())
    
    def test_non_parent_cannot_register_child(self):
        self.client.login(email=self.child.email, password="Watermelon123")
        response = self.client.get(self.reg_page)
        self.assertEqual(response.status_code, 302)
        
    def test_parent_can_access_register_child(self):
        self.client.login(email=self.parent.email, password="Watermelon123")
        response = self.client.get(self.reg_page)
        self.assertEqual(response.status_code, 200)
     
    def test_parent_can_register_child(self):
        self.client.login(email=self.parent.email, password="Watermelon123")
        response = self.client.post(self.reg_page, self.child_form_details, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parent.children.all().first(), self.child)
        self.assertEqual(self.child.parents.all().first(), self.parent)
    
    def test_non_parent_cannot_select_child(self):
        self.client.login(email=self.child.email, password="Watermelon123")
        response = self.client.get(self.sel_page)
        self.assertEqual(response.status_code, 302)
        
    def test_parent_can_access_select_child(self):
        self.client.login(email=self.parent.email, password="Watermelon123")
        response = self.client.get(self.sel_page)
        self.assertEqual(response.status_code, 200)
     
    def test_parent_can_select_child(self):
        self.client.login(email=self.parent.email, password="Watermelon123")
        self.client.post(self.reg_page, self.child_form_details, follow=True)
        self.client.get(reverse('account'))
        response = self.client.post(self.sel_page, {"email": self.child.email}, follow=True)
        self.assertEqual(response.status_code, 200)
        
