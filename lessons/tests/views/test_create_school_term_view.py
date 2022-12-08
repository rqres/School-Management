"""Tests of the Create School Term view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import SchoolTermForm

from lessons.models import SchoolAdmin, SchoolTerm, User


class CreateSchoolTermViewTestCase(TestCase):
    """Tests of the Create School Term view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        self.url = reverse("create_school_term")
        # self.user = User.objects.get(email="default.user@example.org")
        self.director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")
        self.form_input = {
            "start_date": "2022-10-09",
            "end_date": "2022-12-09",
        }

    def test_create_school_term_url(self):
        self.assertEqual(self.url, "/account/school_terms/create/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_create_school_term_as_logged_in_admin(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_school_term.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.assertFalse(form.is_bound)

    def test_unsuccsesful_create_school_term(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        self.form_input["start_date"] = "november"
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_school_term.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_school_term(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count + 1)

        response_url = reverse("school_terms_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "school_terms_list.html")
        term = SchoolTerm.objects.get(start_date=self.form_input["start_date"])
        self.assertEqual(term.start_date.strftime("%Y/%m/%d"), "2022/10/09")
        self.assertEqual(term.end_date.strftime("%Y/%m/%d"), "2022/12/09")

    def test_regular_users_cannot_create_school_terms(self):
        user = User.objects.get(email="default.user@example.org")
        self.client.login(email=user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("log_in") + "?next=" + reverse("create_school_term")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
