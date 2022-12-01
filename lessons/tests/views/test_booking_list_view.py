from django.test import TestCase
from django.urls import reverse
from lessons.models import Booking, Invoice, User, Student, Teacher
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


    def test_booking_list_url(self):
        self.assertEqual(self.url, "/account/bookings/")

    def create_test_bookings(self,booking_count):
        booking = Booking.objects.create(
            num_of_lessons = booking_count,
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics',
            days_between_lessons = 7,
            lesson_duration = 60,
        )
        booking.create_lessons()
        booking.save()
       
       
       
    def test_get_booking_list(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        self.create_test_bookings(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings_list.html")
        
            