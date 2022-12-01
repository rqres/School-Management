from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Booking, User, Student, Teacher
from djmoney.money import Money
import datetime
from django.utils import timezone


class BookingTest(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_student = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user_student)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        self.booking = Booking(
            name=f"{self.student.user.first_name}{self.teacher.user.last_name}Guitar1",
            student=self.student,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            startTime=timezone.now(),
            endTime=timezone.now() + datetime.timedelta(hours=1),
        )
        self.booking.save()
        self.booking_other = Booking(
            name=f"{self.student.user.first_name}{self.teacher.user.last_name}Guitar15",
            student=self.student,
            teacher=self.teacher,
            description="Gutitar lesson on basics continued",
            startTime=timezone.now() + datetime.timedelta(days=1),
            endTime=timezone.now()
            + datetime.timedelta(days=1)
            + datetime.timedelta(hours=1),
        )
        self.booking_other.save()

    def test_valid_booking(self):
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valid")

    def test_name_field_must_not_be_blank(self):
        self.booking.name = ""
        self._assert_booking_is_invalid()

    def test_teacher_field_must_not_be_blank(self):
        self.booking.teacher = None
        self._assert_booking_is_invalid()

    def test_student_field_must_not_be_blank(self):
        self.booking.student = None
        self._assert_booking_is_invalid()

    def test_description_field_must_not_be_blank(self):
        self.booking.description = ""
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
        self.booking.name = "x" * 50
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valids")

    def test_name_cannot_be_over_50_characters_long(self):
        self.booking.name = "x" * 51
        self._assert_booking_is_invalid()

    def test_name_field_is_unique(self):
        self.booking.name = self.booking_other.name
        self._assert_booking_is_invalid()

    def test_student_user_is_valid(self):
        try:
            self.student.full_clean()
        except (ValidationError):
            self.fail("Student should be valid")

    def test_teacher_user_is_valid(self):
        try:
            self.teacher.full_clean()
        except (ValidationError):
            self.fail("Student should be valid")

    def test_invoice_is_valid(self):
        try:
            self.booking.invoice.full_clean()
        except (ValidationError):
            self.fail("Invoice should be valid")

    def test_invoice_price_corresponds_to_duration(self):
        cost = Money(
            round(
                (self.booking.endTime - self.booking.startTime).total_seconds() / 10, 2
            ),
            "GBP",
        )
        self.assertEqual(cost, self.booking.invoice.price)

    def test_invoice_student_num_corresponds_to_student_pk(self):
        self.assertEqual(
            self.booking.invoice.student_num, self.booking.student.pk + 1000
        )

    def test_valid_length_of_booking(self):
        duration = self.booking.endTime - self.booking.startTime
        minutes = round(duration.total_seconds() / 60)
        self.assertTrue(minutes == 30 or minutes == 45 or minutes == 60)

    def test_invalid_length_of_booking(self):
        # self.booking.startTime = datetime.datetime(2022, 11, 10, 11, 0, 0)
        # self.booking.endTime = datetime.datetime(2022, 11, 10, 10, 0, 0)
        self.booking.startTime, self.booking.endTime = (
            self.booking.endTime,
            self.booking.startTime,
        )
        self._assert_booking_is_invalid()

    def test_invalid_long_length_of_booking(self):
        # self.booking.startTime = datetime.datetime(2022, 11, 10, 10, 0, 0)
        # self.booking.endTime = datetime.datetime(2022, 11, 10, 12, 0, 0)
        self.booking.endTime = self.booking.startTime + datetime.timedelta(hours=2)
        self._assert_booking_is_invalid()

    def test_invalid_short_length_of_booking(self):
        # self.booking.startTime = datetime.datetime(2022, 11, 10, 10, 0, 0)
        # self.booking.endTime = datetime.datetime(2022, 11, 10, 10, 20, 0)
        self.booking.endTime = self.booking.startTime + datetime.timedelta(minutes=20)
        self._assert_booking_is_invalid()

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking.full_clean()
