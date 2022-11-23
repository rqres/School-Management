from django.test import TestCase
from django.urls import reverse
from lessons.models import Booking, Invoice, User, Student, Teacher
import datetime
class BookingListTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_user.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse("bookings_list")
        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)


    def test_booking_list_url(self):
        self.assertEqual(self.url, "/account/bookings/")

    def create_test_bookings(self,booking_count):
        for booking_id in range(booking_count):
            
            user_teacher = User.objects.create_user(
            f'teacher{booking_id}@example.org',
            first_name=f'First{booking_id}',
            last_name=f'Last{booking_id}',
            password="TestPassword123",
            )

            user_teacher.is_teacher = True

            new_teacher = Teacher.objects.create(
                user = user_teacher,
                school_name = "Test School"
            )
            booking = Booking.objects.create(
                name = f'{self.student.user.first_name}{new_teacher.user.last_name}Guitar{booking_id}',
                student = self.student,
                teacher = new_teacher,
                description = 'Gutitar lesson on basics',
                startTime = datetime.datetime(2022,11,10,10,0,0),
                endTime = datetime.datetime(2022,11,10,11,0,0),
            )
            booking.save()
            
            
      
    def test_get_booking_list(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        self.create_test_bookings(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings_list.html")
        for booking_id in range(10):
            booking = Booking.objects.get(name = f'JohnLast{booking_id}Guitar{booking_id}')
            self.assertContains(response, f'JohnLast{booking_id}Guitar{booking_id}')
            self.assertContains(response, f'{booking.invoice.urn}')
            self.assertContains(response, 'Gutitar lesson on basics')
            booking_url = reverse('show_booking', kwargs={'booking_id': booking.pk})
            self.assertContains(response, booking_url)
            