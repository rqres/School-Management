"""Tests of the create admin view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from lessons.tests.helpers import LogInTester

from lessons.forms import CreateAdminForm
from lessons.models import SchoolAdmin, User


class CreateAdminViewTestCase(TestCase, LogInTester):
    """Tests of the create admin view"""

    def setUp(self):
        self.url = reverse("create_admin")
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

    def test_create_admin_url(self):
        self.assertEqual(self.url, "/account/all_admins/create/")

    def test_get_create_admin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_admin.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateAdminForm))
        self.assertFalse(form.is_bound)

    def test_unsuccsesful_admin_creation(self):
        self.form_input["email"] = "BAD_EMAIL"
        user_before_count = User.objects.count()
        admin_before_count = SchoolAdmin.objects.count()
        response = self.client.post(self.url, self.form_input)
        user_after_count = User.objects.count()
        admin_after_count = SchoolAdmin.objects.count()
        self.assertEqual(user_after_count, user_before_count)
        self.assertEqual(admin_after_count, admin_before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_admin.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateAdminForm))
        self.assertTrue(form.is_bound)

    def test_successful_admin_creation(self):
        user_before_count = User.objects.count()
        admin_before_count = SchoolAdmin.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        user_after_count = User.objects.count()
        admin_after_count = SchoolAdmin.objects.count()
        self.assertEqual(user_after_count, user_before_count + 1)
        self.assertEqual(admin_after_count, admin_before_count + 1)
        user = User.objects.get(email="bob.dylan@example.org")
        admin = SchoolAdmin.objects.get(user=user)
        self.assertEqual(admin.user.first_name, "Bob")
        self.assertEqual(admin.user.last_name, "Dylan")
        self.assertEqual(admin.user.email, "bob.dylan@example.org")
        self.assertEqual(admin.is_director, True)
        self.assertEqual(admin.can_edit_admins, False)
        self.assertEqual(admin.can_delete_admins, False)
        self.assertEqual(admin.can_create_admins, False)
        self.assertEqual(admin.school_name, "King's College London")
        self.assertTrue(check_password("Watermelon123", admin.user.password))
