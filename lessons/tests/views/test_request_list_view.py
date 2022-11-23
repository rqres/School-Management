"""Tests of the Request for Lessons view"""
from django.test import TestCase
from django.urls import reverse

from lessons.models import RequestForLessons, Student, User


class RequestForLessonsListViewTestCase(TestCase):
    """Tests of the Request for Lessons view"""

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_user.json",
    ]

    def setUp(self):
        self.url = reverse("requests_list")
        self.student = Student.objects.get(user_id="john.doe@example.org")

    def test_request_list_url(self):
        self.assertEqual(self.url, "/account/requests/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_request_list_as_logged_in_user(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "requests_list.html")
        requests_list = response.context["requests"]
        # there should be a list of RequestForLessons objects in the context of the response
        self.assertTrue(isinstance(r, RequestForLessons) for r in requests_list)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("log_in") + "?next=/account/requests/"
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")

    def test_non_students_dont_have_access_to_requests_list(self):
        non_student = User.objects.get(email="default.user@example.org")
        self.client.login(email=non_student.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("home")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "home.html")