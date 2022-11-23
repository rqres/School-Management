from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Booking, Invoice, User , Student , Teacher
import datetime

class BookingTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
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
        self.user_teacher = User.objects.create_user(
            "jane.dave@example.org",
            first_name="Jane",
            last_name="Dave",
            password="TestPassword123",
        )

        self.user_teacher.is_teacher = True

        self.teacher = Teacher.objects.create(
            user = self.user_teacher,
            school_name = "Test School"
        )

        self.invoice = Invoice.objects.create(
            urn = "number"
        )

        self.second_invoice = Invoice.objects.create(
            urn = "another_number"
        )
        self.booking = Booking(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar1',
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics',
            invoice = self.invoice,
            startTime = datetime.datetime(2022,11,10,10,0,0),     
            endTime = datetime.datetime(2022,11,10,11,0,0)
        )
        self.booking_other = Booking(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar15',
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics continued',
            invoice = self.second_invoice,
            startTime = datetime.datetime(2022,11,11,10,0,0),     
            endTime = datetime.datetime(2022,11,11,11,0,0)
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
            self.fail("Test booking should be valid")

    def test_name_field_must_not_be_blank(self):
        self.booking.name = ''
        self._assert_booking_is_invalid()

    def test_teacher_field_must_not_be_blank(self):
        self.booking.teacher = None
        self._assert_booking_is_invalid()

    def test_student_field_must_not_be_blank(self):
        self.booking.student = None
        self._assert_booking_is_invalid()

    def test_description_field_must_not_be_blank(self):
        self.booking.description = ''
        self._assert_booking_is_invalid()

    def test_invoice_field_must_not_be_blank(self):
        self.booking.invoice = None
        self._assert_booking_is_invalid()
    
    def test_startTime_field_must_not_be_blank(self):
        self.booking.startTime = None
        self._assert_booking_is_invalid()

    def test_endTime_field_must_not_be_blank(self):
        self.booking.endTime = None
        self._assert_booking_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.booking.name = 'x' * 50
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valids")
    def test_username_cannot_be_over_50_characters_long(self):
        self.booking.name = 'x' * 51
        self._assert_booking_is_invalid()

    def test_student_user_is_valid(self):
        try:
            self.student.full_clean()
        except(ValidationError):
            self.fail("Student should be valid")

    def test_teacher_user_is_valid(self):
        try:
            self.teacher.full_clean()
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
        self._assert_booking_is_invalid()
    
    def test_invalid_long_length_of_booking(self):
        self.booking.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.booking.endTime = datetime.datetime(2022,11,10,12,0,0)
        self._assert_booking_is_invalid()

    def test_invalid_short_length_of_booking(self):
        self.booking.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.booking.endTime = datetime.datetime(2022,11,10,10,20,0)
        self._assert_booking_is_invalid()

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking.full_clean()