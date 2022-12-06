from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime

class BookingDeletedTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()

        self.url = reverse("delete_booking")
        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022,9,1),
            end_date=datetime.date(2022,10,21),
        )
        create_test_bookings(10)
        self.booking_to_delete = self.student.booking_set.first()

    def test_delete_booking_url(self):
        self.assertEqual(self.url, "/account/bookings/delete/")

    def test_booking_list_has_upadated(self):
        """ New booking list must not contain deleted booking"""
        pass

    def test_delete_booking_message_appears(self):
        # login as admin/director
        # got to booking list and delete
        # check count before and after
        # check message in rendered html has deleted booking's name
        pass

    def test_delete_booking_not_as_director_redirects(self):
        # login as student
        # go to booking list
        # try to delete
        #make sure booking count is the same
        pass