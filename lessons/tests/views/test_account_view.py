from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student, Teacher, SchoolAdmin

class AcccountViewTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(pk=2)
        self.student_user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.student_user)

        self.user_director = User.objects.get(email="bob.dylan@example.org")
        self.director = SchoolAdmin.objects.get(user=self.user_director)
        self.url = reverse("account")
    
    def test_account_url(self):
        self.assertEqual(self.url, "/account/")

    def test_student_user_renders_correctly(self):
        self.client.login(email=self.student_user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_student.html")
        
    def test_director_user_renders_correctly(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_admin.html")


    def test_general_user_renders_correctly(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_user.html")
