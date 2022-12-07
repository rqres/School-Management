from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime

class BookingListTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse("bookings_list")

        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022,9,1),
            end_date=datetime.date(2022,10,21),
        )


    def test_booking_list_url(self):
        self.assertEqual(self.url, "/account/bookings/")

    def test_get_booking_list(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        create_test_bookings(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings_list.html")
        for booking_id in range(10):
            booking = Booking.objects.get(pk=booking_id+1)   
            self.assertContains(response, booking.num_of_lessons)
            self.assertContains(response, booking.description)
            self.assertContains(response, booking.invoice.urn)
            self.assertContains(response, booking.user.email)
            self.assertContains(response, booking.teacher.user.email)

    def test_cannot_get_booking_when_not_logged_in(self):
        pass


