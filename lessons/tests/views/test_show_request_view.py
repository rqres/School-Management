"""Tests of the Show Request view"""
from django.test import TestCase
from django.urls import reverse

from lessons.models import RequestForLessons, User


class ShowRequestForLessonsViewTestCase(TestCase):
    """Tests of the Show Request view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.req = RequestForLessons.objects.get(pk=1)
        self.url = reverse("show_request", kwargs={"id": self.req.pk})
        self.user = User.objects.get(email="default.user@example.org")

    def test_show_request_url(self):
        self.assertEqual(self.url, "/account/requests/" + str(self.req.pk) + "/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_request_list_as_logged_in_regular_user(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "show_request.html")
        lessons_request = response.context["lessons_request"]
        # there should be a list of RequestForLessons objects in the context of the response
        self.assertTrue(isinstance(lessons_request, RequestForLessons))

    def test_404_if_request_does_not_exist(self):
        self.req.delete()
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = (
            reverse("log_in")
            + "?next="
            + reverse("show_request", kwargs={"id": self.req.pk})
        )
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
