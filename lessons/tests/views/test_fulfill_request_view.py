"""Tests of the Fulfill Request view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import FulfillLessonRequestForm

from lessons.models import RequestForLessons, SchoolAdmin, Student, User


class FulfillRequestViewTestCase(TestCase):
    """Tests of the Fulfill Request view"""

    fixtures = [
        "lessons/tests/fixtures/default_request.json",
        "lessons/tests/fixtures/default_director.json",
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_user.json",
    ]

    def setUp(self):
        self.req_pk = RequestForLessons.objects.get(pk=1).pk
        self.url = reverse("fulfill_request", kwargs={"id": self.req_pk})
        self.director = SchoolAdmin.objects.get(pk=6)

    def test_fulfill_request_url(self):
        self.assertEqual(self.url, f"/account/requests/{self.req_pk}/fulfill/")

    # test an HTTP GET request to this page when admin logged in
    def test_GET_fulfill_request_as_logged_in_admin(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fulfill_request_form.html")
        request_id = response.context["request_id"]
        user_name = response.context["user_name"]
        form = response.context["form"]
        self.assertTrue(isinstance(request_id, int))
        self.assertTrue(isinstance(user_name, str))
        self.assertTrue(isinstance(form, FulfillLessonRequestForm))

    def test_user_permission_denied_if_not_admin(self):
        default_student = Student.objects.get(pk=1)
        self.client.login(email=default_student.user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
