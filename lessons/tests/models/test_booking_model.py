from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import SchoolTerm, Booking, Invoice, User, Student, Teacher
from djmoney.money import Money
import datetime


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

        self.invoice = Invoice(
            user=self.user_student,
            student_num=self.student.user.pk + 1000,
            invoice_num=Invoice.objects.filter(student_num=self.student.user.pk).count()
            + 1,
            price=Money(10, "GBP"),
        )
        self.invoice.save()

        self.booking = Booking(
            num_of_lessons=10,
            user=self.user_student,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            days_between_lessons=7,
            lesson_duration=60,
        )
        self.booking.save()
        self.booking_other = Booking(
            num_of_lessons=10,
            user=self.user_student,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            days_between_lessons=7,
            lesson_duration=60,
        )
        self.booking_other.save()

        SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )

    def test_valid_booking(self):
        self._assert_booking_is_valid()

    def test_num_of_lessons_field_must_not_be_blank(self):
        self.booking.num_of_lessons = None
        self._assert_booking_is_invalid()

    def test_teacher_field_must_not_be_blank(self):
        self.booking.teacher = None
        self._assert_booking_is_invalid()

    def test_user_field_must_not_be_blank(self):
        self.booking.user = None
        self._assert_booking_is_invalid()

    # TODO:
    def dont_test_description_field_must_not_be_blank(self):
        self.booking.description = ""
        self._assert_booking_is_invalid()

    def test_days_between_lessons_field_must_not_be_blank(self):
        self.booking.days_between_lessons = None
        self._assert_booking_is_invalid()

    def test_lesson_duration_field_must_not_be_blank(self):
        self.booking.lesson_duration = None
        self._assert_booking_is_invalid()

    def test_invoice_field_must_not_be_blank(self):
        self.booking.invoice = None
        self._assert_booking_is_invalid()

    def test_invoice_field_accepts_valid_invoice(self):
        self.booking.invoice = self.invoice
        try:
            self.invoice.full_clean()
        except (ValidationError):
            self.fail("Student should be valid")

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

    def test_valid_lesson_duration(self):
        self.assertTrue(
            self.booking.lesson_duration == 30
            or self.booking.lesson_duration == 45
            or self.booking.lesson_duration == 60
        )

    def test_create_invoice_for_booking(self):
        self.booking.create_invoice()
        try:
            self.invoice.full_clean()
        except (ValidationError):
            self.fail("Student should be valid")
        self.assertEqual(self.booking.invoice.student_num, self.student.pk + 1000)
        self.assertEqual(self.booking.invoice.user, self.user_student)
        costOfBooking = Money(
            self.booking.lesson_duration * self.booking.num_of_lessons / 10, "GBP"
        )
        self.assertEqual(self.booking.invoice.price, costOfBooking)

    def test_update_invoice_when_change_in_lesson_duration(self):
        self.booking.invoice = self.invoice
        self.booking.lesson_duration = 30
        self.booking.update_invoice()
        costOfBooking = Money(
            self.booking.lesson_duration * self.booking.num_of_lessons / 10, "GBP"
        )
        self.assertEqual(self.booking.invoice.price, costOfBooking)

    def test_invoice_unique_to_booking(self):
        pass

    def test_create_lessons_for_booking(self):
        self.booking.create_lessons()
        lessons = self.booking.lesson_set.all()
        self.assertEqual(lessons.count(), self.booking.num_of_lessons)
        for lesson in lessons:
            pass

    def test_update_lessons_for_booking(self):
        pass

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def _assert_booking_is_valid(self):
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valid")
