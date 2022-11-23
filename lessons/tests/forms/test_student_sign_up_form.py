from django.test import TestCase
from django import forms
from django.contrib.auth.hashers import check_password

from lessons.forms import StudentSignUpForm
from lessons.models import Student, User

# Create your tests here.


class StudentSignUpFormTestCase(TestCase):
    """Unit tests for the sign up form"""

    def setUp(self):
        self.form_input = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.org",
            "school_name": "King's College London",
            "password1": "Watermelon123",
            "password2": "Watermelon123",
        }

    # Form accepts valid input
    def test_valid_sign_up_form(self):
        form = StudentSignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Form has necessary fields
    def test_form_has_necessary_fields(self):
        form = StudentSignUpForm()
        self.assertIn("first_name", form.fields)
        self.assertIn("last_name", form.fields)
        self.assertIn("email", form.fields)
        email_field = form.fields["email"]
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn("password1", form.fields)
        password1_widget = form.fields["password1"].widget
        self.assertTrue(isinstance(password1_widget, forms.PasswordInput))
        self.assertIn("password2", form.fields)
        password2_widget = form.fields["password2"].widget
        self.assertTrue(isinstance(password2_widget, forms.PasswordInput))

    # No bad input
    def test_form_uses_model_validation(self):
        self.form_input["email"] = "bademail"
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Password uses correct format
    def test_pw_must_contain_uppercase(self):
        self.form_input["password1"] = "watermelon123"
        self.form_input["password2"] = "watermelon123"
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_pw_must_contain_lowercase(self):
        self.form_input["password1"] = "WATERMELON123"
        self.form_input["password2"] = "WATERMELON123"
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_pw_must_contain_number(self):
        self.form_input["password1"] = "WatermelonABC"
        self.form_input["password2"] = "WatermelonABC"
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirm_are_identical(self):
        self.form_input["password2"] = "WrongWatermelon123"
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = StudentSignUpForm(data=self.form_input)
        before_count_students = Student.objects.count()
        before_count_users = User.objects.count()
        form.save()
        after_count_students = Student.objects.count()
        after_count_users = User.objects.count()
        self.assertEqual(after_count_students, before_count_students + 1)
        self.assertEqual(after_count_users, before_count_users + 1)
        user = User.objects.get(email="john.doe@example.org")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john.doe@example.org")
        self.assertTrue(check_password("Watermelon123", user.password))
