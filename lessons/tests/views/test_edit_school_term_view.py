"""Tests of the Edit School Term view"""
from django.test import TestCase
from django.urls import reverse
import datetime
from lessons.forms import RequestForLessonsForm, SchoolTermForm

from lessons.models import RequestForLessons, SchoolAdmin, SchoolTerm, User


class EditSchoolTermViewTestCase(TestCase):
    """Tests of the Edit School Term view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        self.term = SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )
        self.url = reverse("edit_school_term", kwargs={"id": self.term.pk})
        # self.user = User.objects.get(email="default.user@example.org")
        self.director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")
        self.form_input = {
            "start_date": "2022-10-09",
            "end_date": "2022-12-09",
        }

    def test_edit_school_term_url(self):
        self.assertEqual(self.url, f"/account/school_terms/{self.term.pk}/edit/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_edit_term_as_logged_in_admin(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_school_term.html")
        form = response.context["form"]
        school_term_id = response.context["school_term_id"]
        self.assertTrue(isinstance(form, SchoolTermForm))
        # form should be bound with previous data when editing
        self.assertTrue(form.is_valid)
        # make sure request id corresponds to our request
        self.assertEqual(school_term_id, self.term.pk)

    def test_unsuccsesful_edit_term(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        self.form_input["start_date"] = "november"
        before = SchoolTerm.objects.get(pk=1)
        response = self.client.post(self.url, self.form_input)
        after = SchoolTerm.objects.get(pk=1)
        # an unsuccessful edit should not alter a field
        self.assertEqual(before.start_date, after.start_date)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_school_term.html")
        form = response.context["form"]
        school_term_id = response.context["school_term_id"]
        self.assertTrue(isinstance(form, SchoolTermForm))
        # form should be bound with previous data when editing
        self.assertTrue(form.is_bound)
        # make sure request id corresponds to our request
        self.assertEqual(school_term_id, self.term.pk)

    def test_successful_edit_school_term(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        before = SchoolTerm.objects.get(pk=1)
        response = self.client.post(self.url, self.form_input, follow=True)
        after = SchoolTerm.objects.get(pk=1)
        # a successful edit should alter a field
        self.assertNotEqual(before.start_date, after.start_date)
        response_url = reverse("school_terms_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "school_terms_list.html")
        trm = SchoolTerm.objects.get(pk=1)
        self.assertEqual(trm.start_date.strftime("%Y/%m/%d"), "2022/10/09")
        self.assertEqual(trm.end_date.strftime("%Y/%m/%d"), "2022/12/09")

    def test_regular_users_cannot_edit_terms(self):
        user = User.objects.get(email="default.user@example.org")
        self.client.login(email=user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = (
            reverse("log_in")
            + "?next="
            + reverse("edit_school_term", kwargs={"id": self.term.pk})
        )
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
