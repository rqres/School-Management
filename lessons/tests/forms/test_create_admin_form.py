from django.test import TestCase
from django import forms
from django.contrib.auth.hashers import check_password

from lessons.forms import CreateAdminForm
from lessons.models import SchoolAdmin, User

# Create your tests here.


class CreateAdminFormTestCase(TestCase):
    """Unit tests for the create admin form"""

    def setUp(self):
        self.form_input = {
            "first_name": "Bob",
            "last_name": "Dylan",
            "email": "bob.dylan@example.org",
            "school_name": "King's College London",
            "is_director": True,
            "can_edit_admins" : False,
            "can_create_admins" : False,
            "can_delete_admins" : False,
            "password1": "Watermelon123",
            "password2": "Watermelon123",
        }

    # Form accepts valid input
    def test_valid_create_Admin_form(self):
        form = CreateAdminForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Form has necessary fields
    def test_form_has_necessary_fields(self):
        form = CreateAdminForm()
        self.assertIn("first_name", form.fields)
        self.assertIn("last_name", form.fields)
        self.assertIn("email", form.fields)
        email_field = form.fields["email"]
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn("school_name", form.fields)
        school_name_field = form.fields["school_name"]
        self.assertTrue(isinstance(school_name_field, forms.CharField))
        self.assertIn("is_director", form.fields)
        is_director_field = form.fields["is_director"]
        self.assertTrue(isinstance(is_director_field, forms.BooleanField))
        self.assertIn("can_create_admins", form.fields)
        create_admin_field = form.fields["can_create_admins"]
        self.assertTrue(isinstance(create_admin_field, forms.BooleanField))
        self.assertIn("can_edit_admins", form.fields)
        edit_admin_field = form.fields["can_edit_admins"]
        self.assertTrue(isinstance(edit_admin_field, forms.BooleanField))
        self.assertIn("can_delete_admins", form.fields)
        delete_admin_field = form.fields["can_delete_admins"]
        self.assertTrue(isinstance(delete_admin_field, forms.BooleanField))
        self.assertIn("password1", form.fields)
        password1_widget = form.fields["password1"].widget
        self.assertTrue(isinstance(password1_widget, forms.PasswordInput))
        self.assertIn("password2", form.fields)
        password2_widget = form.fields["password2"].widget
        self.assertTrue(isinstance(password2_widget, forms.PasswordInput))

    # No bad input
    def test_form_uses_model_validation(self):
        self.form_input["email"] = "bademail"
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Password uses correct format
    def test_pw_must_contain_uppercase(self):
        self.form_input["password1"] = "watermelon123"
        self.form_input["password2"] = "watermelon123"
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_pw_must_contain_lowercase(self):
        self.form_input["password1"] = "WATERMELON123"
        self.form_input["password2"] = "WATERMELON123"
        form =  CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_pw_must_contain_number(self):
        self.form_input["password1"] = "WatermelonABC"
        self.form_input["password2"] = "WatermelonABC"
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirm_are_identical(self):
        self.form_input["password2"] = "WrongWatermelon123"
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateAdminForm(data=self.form_input)
        before_count_admins = SchoolAdmin.objects.count()
        before_count_users = User.objects.count()
        form.save()
        after_count_admins = SchoolAdmin.objects.count()
        after_count_users = User.objects.count()
        self.assertEqual(after_count_admins, before_count_admins + 1)
        self.assertEqual(after_count_users, before_count_users + 1)
        user = User.objects.get(email="bob.dylan@example.org")
        self.assertEqual(user.first_name, "Bob")
        self.assertEqual(user.last_name, "Dylan")
        self.assertEqual(user.email, "bob.dylan@example.org")
        self.assertTrue(check_password("Watermelon123", user.password))
