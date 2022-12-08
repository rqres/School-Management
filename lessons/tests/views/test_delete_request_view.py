"""Tests of the Delete Request for Lessons view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForLessonsForm

from lessons.models import RequestForLessons, SchoolAdmin, User


class DeleteRequestForLessonsViewTestCase(TestCase):
    """Tests of the Delete Request for Lessons view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        # "lessons/tests/fixtures/default_director.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.req = RequestForLessons.objects.get(pk=1)
        self.url = reverse("delete_request", kwargs={"id": self.req.pk})
        self.user = User.objects.get(email="default.user@example.org")
        # self.form_input = {
        #     "no_of_lessons": 20,
        #     "availability_field": ["TUE", "SAT", "SUN"],
        #     "days_between_lessons": 10,
        #     "lesson_duration": 15,
        #     "other_info": "Edited info",
        # }

    def test_delete_request_url(self):
        self.assertEqual(self.url, f"/account/requests/{self.req.pk}/delete/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_delete_request_as_logged_in_user(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse("requests_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "requests_list.html")

    def test_unsuccsesful_delete_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        # test resource not found
        self.req.delete()
        response = self.client.get(self.url)
        # if resource does not exist, trying to delete it should raise 404
        self.assertEqual(response.status_code, 404)

    def test_successful_delete_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        before_count = RequestForLessons.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = RequestForLessons.objects.count()
        self.assertEqual(before_count - 1, after_count)
        response_url = reverse("requests_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "requests_list.html")

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = (
            reverse("log_in")
            + "?next="
            + reverse("delete_request", kwargs={"id": self.req.pk})
        )
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
