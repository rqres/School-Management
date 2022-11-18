from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Booking, Invoice, User
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
        self.invoice =Invoice.objects.create(
            urn = "number"
        )
        self.booking = Booking(
            student = self.user,
            invoice = self.invoice,
            startTime = datetime.time(10,0,0),
            endTime = datetime.time(12,0,0)
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


