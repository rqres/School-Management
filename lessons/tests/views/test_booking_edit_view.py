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

    def test_booking_edit_url(self):
        pass

    def test_booking_edit_redirects_when_not_director(self):
        pass

    def test_successful_booking_edit(self):
        pass

    def test_unsuccessful_booking_edit(self):
        pass
