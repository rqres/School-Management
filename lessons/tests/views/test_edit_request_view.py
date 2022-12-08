"""Tests of the Edit Request for Lessons view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForLessonsForm

from lessons.models import RequestForLessons, SchoolAdmin, User


class EditRequestForLessonsViewTestCase(TestCase):
    """Tests of the Edit Request for Lessons view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.req = RequestForLessons.objects.get(pk=1)
        self.url = reverse("edit_request", kwargs={"id": self.req.pk})
        self.user = User.objects.get(email="default.user@example.org")
        self.form_input = {
            "no_of_lessons": 20,
            "availability_field": ["TUE", "SAT", "SUN"],
            "days_between_lessons": 10,
            "lesson_duration": 15,
            "other_info": "Edited info",
        }

    def test_edit_request_url(self):
        self.assertEqual(self.url, f"/account/requests/{self.req.pk}/edit/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_edit_request_as_logged_in_user(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_request.html")
        form = response.context["form"]
        request_id = response.context["request_id"]
        self.assertTrue(isinstance(form, RequestForLessonsForm))
        # form should be bound with previous data when editing
        self.assertTrue(form.is_valid)
        # make sure request id corresponds to our request
        self.assertEqual(request_id, self.req.pk)

    def test_unsuccsesful_edit_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        self.form_input["no_of_lessons"] = "ten"
        before = RequestForLessons.objects.get(pk=1)
        response = self.client.post(self.url, self.form_input)
        after = RequestForLessons.objects.get(pk=1)
        # an unsuccessful edit should not alter a field
        self.assertEqual(before.no_of_lessons, after.no_of_lessons)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_request.html")
        form = response.context["form"]
        request_id = response.context["request_id"]
        self.assertTrue(isinstance(form, RequestForLessonsForm))
        # form should be bound with previous data when editing
        self.assertTrue(form.is_bound)
        # make sure request id corresponds to our request
        self.assertEqual(request_id, self.req.pk)

    def test_successful_edit_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        before = RequestForLessons.objects.get(pk=1)
        response = self.client.post(self.url, self.form_input, follow=True)
        after = RequestForLessons.objects.get(pk=1)
        # a successful edit should alter a field
        self.assertNotEqual(before.no_of_lessons, after.no_of_lessons)
        response_url = reverse("requests_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "requests_list.html")
        req = RequestForLessons.objects.get(pk=1)
        self.assertEqual(req.no_of_lessons, 20)
        self.assertEqual(req.days_between_lessons, 10)
        self.assertEqual(req.lesson_duration, 15)
        self.assertEqual(req.other_info, "Edited info")
        self.assertEqual(req.availability, "TUE,SAT,SUN")

    def test_admins_cannot_edit_requests(self):
        director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")
        self.client.login(email=director.user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = (
            reverse("log_in")
            + "?next="
            + reverse("edit_request", kwargs={"id": self.req.pk})
        )
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
