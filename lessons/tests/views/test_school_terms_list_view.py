"""Tests of the School Terms List view"""
from django.test import TestCase
from django.urls import reverse

from lessons.models import SchoolAdmin, SchoolTerm, User


class SchoolTermsListView(TestCase):
    """Tests of the School Terms List view"""

    fixtures = [
        "lessons/tests/fixtures/default_director.json",
        "lessons/tests/fixtures/default_user.json",
    ]

    def setUp(self):
        self.url = reverse("school_terms_list")
        self.director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")

    def test_request_list_url(self):
        self.assertEqual(self.url, "/account/school_terms/")

    # test an HTTP GET request to this page when director is logged in
    def test_GET_request_list_as_logged_in_user(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "school_terms_list.html")
        school_terms_list = response.context["school_terms"]
        # there should be a list of RequestForLessons objects
        # in the context of the response
        self.assertTrue(isinstance(st, SchoolTerm) for st in school_terms_list)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("log_in") + "?next=" + reverse("school_terms_list")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")

    # TODO:
    def dont_test_non_admins_dont_have_access_to_terms_list(self):
        non_admin = User.objects.get(email="default.user@example.org")
        self.client.login(email=non_admin.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("home")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "home.html")
