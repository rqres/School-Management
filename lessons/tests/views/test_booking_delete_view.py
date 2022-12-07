from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolAdmin, SchoolTerm, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime

class BookingDeletedTest(TestCase):

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
            start_date=datetime.date(2022,9,1),
            end_date=datetime.date(2022,10,21),
        )
        create_test_bookings(10)
        self.booking_to_delete = self.student.booking_set.first()
        self.booking_name = str(self.booking_to_delete)
        self.booking_invoice = self.booking_to_delete.invoice.urn
        self.url = reverse("delete_booking",  kwargs={'booking_id': self.booking_to_delete.id})

    def test_delete_booking_url(self):
        self.assertEqual(self.url, "/account/bookings/delete/1/")

    def test_booking_list_has_updated(self):
        """ New booking list must not contain deleted booking"""
        self.client.login(email=self.director.user.email, password="Watermelon123")
        num_of_bookings_before = Booking.objects.count()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking_name)
        response_url = reverse("bookings_list")
        new_response = self.client.get(response_url)
        self.assertEqual(new_response.status_code, 200)
        num_of_bookings_after = Booking.objects.count()
        self.assertEqual(num_of_bookings_before, num_of_bookings_after+1)
        #self.assertNotContains(new_response, self.booking_invoice)

    def test_delete_booking_message_appears(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have deleted the booking :")
        self.assertContains(response, self.booking_name)


    def test_delete_booking_not_as_director_redirects(self):
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
        
        