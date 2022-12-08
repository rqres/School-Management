"""Tests of the Create Request for Lessons view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForLessonsForm

from lessons.models import RequestForLessons, SchoolAdmin, User


class CreateRequestForLessonsViewTestCase(TestCase):
    """Tests of the Create Request for Lessons view"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        self.url = reverse("create_request")
        self.user = User.objects.get(email="default.user@example.org")
        self.form_input = {
            "no_of_lessons": 10,
            "availability_field": ["MON", "TUE", "SAT"],
            "days_between_lessons": 7,
            "lesson_duration": 60,
            "other_info": "This is some info",
        }

    def test_create_request_url(self):
        self.assertEqual(self.url, "/account/requests/create/")

    # test an HTTP GET request to this page when user logged in
    def test_GET_request_list_as_logged_in_user(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_request.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, RequestForLessonsForm))
        self.assertFalse(form.is_bound)

    def test_unsuccsesful_create_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        self.form_input["no_of_lessons"] = "ten"
        before_count = RequestForLessons.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = RequestForLessons.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_request.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, RequestForLessonsForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_request(self):
        self.client.login(email=self.user.email, password="Watermelon123")
        before_count = RequestForLessons.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = RequestForLessons.objects.count()
        self.assertEqual(after_count, before_count + 1)

        response_url = reverse("requests_list")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "requests_list.html")
        req = RequestForLessons.objects.get(user=self.user)
        self.assertEqual(req.no_of_lessons, 10)
        self.assertEqual(req.days_between_lessons, 7)
        self.assertEqual(req.lesson_duration, 60)
        self.assertEqual(req.other_info, "This is some info")
        self.assertEqual(req.availability, "MON,TUE,SAT")

    def test_admins_cannot_create_requests(self):
        director = SchoolAdmin.objects.get(user__email="bob.dylan@example.org")
        self.client.login(email=director.user.email, password="Watermelon123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_is_redirected_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("log_in") + "?next=" + reverse("create_request")
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")
