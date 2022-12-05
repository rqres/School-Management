from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm, Booking, User, Student, Teacher
import datetime
from django.utils import timezone


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

    def create_test_bookings(self,booking_count):
        
        for booking_id in range(booking_count):
            user_teacher = User.objects.create_user(
                f"teacher{booking_id}@example.org",
                first_name=f"First{booking_id}",
                last_name=f"Last{booking_id}",
                password="TestPassword123",
            )

            user_teacher.is_teacher = True

            new_teacher = Teacher.objects.create(
                user=user_teacher, school_name="Test School"
            )
            booking = Booking.objects.create(
                num_of_lessons = booking_count,
                student = self.student,
                teacher = new_teacher,
                description = f'Gutitar lesson on basics{booking_id}',
                days_between_lessons = 7,
                lesson_duration = 60,
            )
            booking.create_lessons()
            booking.create_invoice()
            booking.save()

    def test_get_booking_list(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        self.create_test_bookings(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings_list.html")
        for booking_id in range(10):
            booking = Booking.objects.get(pk=booking_id+1)   
            self.assertContains(response, booking.num_of_lessons)
            self.assertContains(response, booking.description)
            self.assertContains(response, booking.invoice.urn)
            self.assertContains(response, booking.student.user.first_name)
            self.assertContains(response, booking.teacher.user.first_name)


