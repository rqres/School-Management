"""Tests of the Request for Lessons List view"""
from django.test import TestCase
from django.urls import reverse

from lessons.models import RequestForLessons, SchoolAdmin, User


class RequestForLessonsListViewTestCase(TestCase):
    """Tests of the Request for Lessons List view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        self.url = reverse("requests_list")
        self.user = User.objects.get(email="default.user@example.org")
        self.director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")

    def test_request_list_url(self):
        self.assertEqual(self.url, "/account/requests/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_request_list_as_logged_in_regular_user(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "requests_list.html")
        requests_list = response.context["requests"]
        # there should be a list of RequestForLessons objects in the context of the response
        self.assertTrue(isinstance(r, RequestForLessons) for r in requests_list)
        # if logged in as a user, only user's requests should be displayed
        for r in requests_list:
            self.assertEqual(self.user, r.user)

    def test_GET_request_list_as_logged_in_admin(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "requests_list.html")
        requests_list = response.context["requests"]
        # there should be a list of RequestForLessons objects in the context of the response
        self.assertTrue(isinstance(r, RequestForLessons) for r in requests_list)
        # if logged in as an admin, all requests should be displayed
        self.assertEqual(len(RequestForLessons.objects.all()), len(requests_list))

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("log_in") + "?next=" + reverse("requests_list")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
