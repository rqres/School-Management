from django.test import TestCase
from django.urls import reverse
from lessons.models import Booking, Invoice, User, Student, Teacher
import datetime
class BookingListTest(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('booking_list')
        self.user_student = User.objects.create_user(
            "john.doe@example.org",
            first_name="John",
            last_name="Doe",
            password="TestPassword123",
        )

        self.user_student.is_student = True

        self.student = Student.objects.create(
            user = self.user_student,
            school_name = "Test School"
        )

    def test_booking_list_url(self):
        self.assertEqual(self.url, '/bookings/')

    def create_test_bookings(self,booking_count):
        for booking_id in range(booking_count):
            bookingUser = User.objects.create_user(
                f'{booking_id}@test.org',
                first_name=f'First{booking_id}',
                last_name=f'Last{booking_id}',
                password='Password123',
            )

            bookingUser.is_student = True

            new_student = Student.objects.create(
                            user = bookingUser,
                            school_name = "Test School"
                        )
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

            Booking.objects.create(
                name = f'{new_student.user.first_name}{new_teacher.user.last_name}Guitar{booking_id}',
                student = new_student,
                teacher = new_teacher,
                description = 'Gutitar lesson on basics',
                invoice =  Invoice.objects.create(
                    urn = f'number{booking_id}'
                ),
                startTime = datetime.datetime(2022,11,10,10,0,0),
                endTime = datetime.datetime(2022,11,10,11,0,0),
            )
      
    def test_get_booking_list(self):
        self.client.login(email= self.student.user.email, password='TestPassword123')
        self.create_test_bookings(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_list.html')
        for booking_id in range(10):
            self.assertContains(response, f'First{booking_id}Last{booking_id}Guitar{booking_id}')
            self.assertContains(response, 'Gutitar lesson on basics')
            self.assertContains(response, f'number{booking_id}')
            
            booking = Booking.objects.get(name = f'First{booking_id}Last{booking_id}Guitar{booking_id}')
            booking_url = reverse('show_booking', kwargs={'booking_id': booking.pk})
            self.assertContains(response, booking_url)
            