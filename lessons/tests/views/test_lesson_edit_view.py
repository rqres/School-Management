from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolAdmin, SchoolTerm, Lesson, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime


class LessonEditTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        self.user_director = User.objects.get(email="bob.dylan@example.org")
        self.director = SchoolAdmin.objects.get(user=self.user_director)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )
        create_test_bookings(10)
        self.booking_to_edit = self.user.booking_set.first()
        self.lesson_to_edit = self.booking_to_edit.lesson_set.first()
        self.url = reverse(
            "edit_lesson", kwargs={"booking_id": self.booking_to_edit.id, "lesson_id":self.lesson_to_edit.id}
        )
        self.data = {
            "name": "Name of lesson",
            "date": "2022-10-10",
            "startTime": "10:00:00",
            "description": "This is the updated lesson.",
        }

    def test_lesson_edit_url(self):
        self.assertEqual(self.url, "/account/bookings/1/10/")

    def test_lesson_edit_redirects_when_not_director(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        num_of_bookings_before = Booking.objects.count()
        response = self.client.get(self.url)
        redirect_url = "/account/"
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        num_of_bookings_after = Booking.objects.count()
        self.assertEqual(num_of_bookings_before, num_of_bookings_after)

    def test_successful_lesson_edit(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.post(self.url, self.data, follow=True)
        updated_lesson = Lesson.objects.get(id=self.lesson_to_edit.id)
        self.assertEqual(updated_lesson.name, self.data["name"])
        self.assertEqual(str(updated_lesson.date), self.data["date"])
        self.assertEqual(str(updated_lesson.startTime), self.data["startTime"])
        self.assertEqual(updated_lesson.description, self.data["description"])
        self.assertTemplateUsed(response, "show_booking.html")

    def test_unsuccessful_lesson_edit(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        self.data["date"] =  ""
        response = self.client.post(self.url, self.data, follow=True)
        updated_lesson = Lesson.objects.get(id=self.lesson_to_edit.id)
        self.assertTemplateUsed(response, "edit_lesson.html")