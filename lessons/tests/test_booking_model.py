from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Booking, Invoice, User , Student
import datetime

class BookingTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            "john.doe@example.org",
            first_name="John",
            last_name="Doe",
            password="TestPassword123",
        )

        self.user.is_student = True

        self.student = Student.objects.create(
            user = self.user,
            school_name = "Test School"
        )
        self.invoice =Invoice.objects.create(
            urn = "number"
        )
        self.booking = Booking(
            student = self.student,
            invoice = self.invoice,
            startTime = datetime.datetime(2022,11,10,10,0,0),     
            endTime = datetime.datetime(2022,11,10,11,0,0)
            )

    def test_valid_invoice(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("Test invoice should be valids")

    def test_valid_booking(self):
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valids")

    def test_student_field_must_not_be_blank(self):
        self.booking.student = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_invoice_field_must_not_be_blank(self):
        self.booking.invoice = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()
    
    def test_startTime_field_must_not_be_blank(self):
        self.booking.startTime = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_endTime_field_must_not_be_blank(self):
        self.booking.endTime = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_student_user_is_valid(self):
        try:
            self.student.full_clean()
        except(ValidationError):
            self.fail("Student should be valid")

    def test_valid_length_of_booking(self):
        duration = self.booking.endTime - self.booking.startTime
        minutes = duration.total_seconds()/60
        self.assertTrue(minutes == 30 or 
                        minutes == 45 or 
                        minutes == 60 )

    def test_invalid_length_of_booking(self):
        self.booking.startTime = datetime.datetime(2022,11,10,11,0,0)
        self.booking.endTime = datetime.datetime(2022,11,10,10,0,0)
        with self.assertRaises(ValidationError):
            self.booking.full_clean()
    
    def test_invalid_long_length_of_booking(self):
        self.booking.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.booking.endTime = datetime.datetime(2022,11,10,12,0,0)
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_invalid_short_length_of_booking(self):
        self.booking.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.booking.endTime = datetime.datetime(2022,11,10,10,20,0)
        with self.assertRaises(ValidationError):
            self.booking.full_clean()