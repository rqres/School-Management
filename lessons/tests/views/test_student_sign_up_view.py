"""Tests of the sign up view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LogInTester

from lessons.forms import StudentSignUpForm
from lessons.models import Student, User


class StudentSignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view"""

    def setUp(self):
        self.url = reverse("sign_up_student")
        self.form_input = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.org",
            "school_name": "King's College London",
            "password1": "Watermelon123",
            "password2": "Watermelon123",
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, "/sign_up/student/")

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sign_up_student.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, StudentSignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccsesful_sign_up(self):
        self.form_input["email"] = "BAD_EMAIL"
        user_before_count = User.objects.count()
        student_before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input)
        user_after_count = User.objects.count()
        student_after_count = Student.objects.count()
        self.assertEqual(user_after_count, user_before_count)
        self.assertEqual(student_after_count, student_before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sign_up_student.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, StudentSignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.is_logged_in())

    def test_successful_sign_up(self):
        user_before_count = User.objects.count()
        student_before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        user_after_count = User.objects.count()
        student_after_count = Student.objects.count()
        self.assertEqual(user_after_count, user_before_count + 1)
        self.assertEqual(student_after_count, student_before_count + 1)

        response_url = reverse("account")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "account.html")
        user = User.objects.get(email="john.doe@example.org")
        student = Student.objects.get(user=user)
        self.assertEqual(student.user.first_name, "John")
        self.assertEqual(student.user.last_name, "Doe")
        self.assertEqual(student.user.email, "john.doe@example.org")
        self.assertEqual(student.school_name, "King's College London")
        self.assertTrue(check_password("Watermelon123", student.user.password))
        self.assertTrue(self.is_logged_in())
