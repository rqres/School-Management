from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolAdmin, SchoolTerm, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime


class BookingEditTest(TestCase):

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
        self.url = reverse(
            "edit_booking", kwargs={"booking_id": self.booking_to_edit.id}
        )
        self.data = {
            "teacher": self.teacher,
            "num_of_lessons": 14,
            "days_between_lessons": 7,
            "lesson_duration": 60,
            "description": "Edited booking"
        }

    def test_booking_edit_url(self):
        self.assertEqual(self.url, "/account/bookings/edit/1/")

    def test_booking_edit_redirects_when_not_director(self):
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

    def donot_test_successful_booking_edit(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.post(self.url, self.data, follow=True)
        updated_booking = Booking.objects.get(id=self.booking_to_edit.id)
        self.assertEqual(updated_booking.teacher, self.data["teacher"])
        self.assertEqual(str(updated_booking.num_of_lessons), self.data["num_of_lessons"])
        self.assertEqual(str(updated_booking.days_between_lessons), self.data["days_between_lessons"])
        self.assertEqual(str(updated_booking.lesson_duration), self.data["lesson_duration"])
        self.assertEqual(updated_booking.description, self.data["description"])
        self.assertTemplateUsed(response, "bookings_list.html")

    def test_unsuccessful_booking_edit(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        self.data["teacher"] =  ""
        response = self.client.post(self.url, self.data, follow=True)
        updated_booking = Booking.objects.get(id=self.booking_to_edit.id)
        self.assertTemplateUsed(response, "edit_booking.html")
