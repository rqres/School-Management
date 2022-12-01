from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Booking, Invoice, User , Student , Teacher
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

        self.booking = Booking(
            num_of_lessons = 10,
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics',
            days_between_lessons = 7,
            lesson_duration = 60,
        )
        self.booking.save()
        self.booking_other = Booking(
            num_of_lessons = 10,
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics',
            days_between_lessons = 7,
            lesson_duration = 60,
        )
        self.booking_other.save()

    def test_valid_booking(self):
        try:
            self.booking.full_clean()
        except ValidationError:
            self.fail("Test booking should be valid")

    def test_num_of_lessons_field_must_not_be_blank(self):
        self.booking.num_of_lessons = None
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
    
    def test_days_between_lessons_field_must_not_be_blank(self):
        self.booking.days_between_lessons = None
        self._assert_booking_is_invalid()

    def test_lesson_duration_field_must_not_be_blank(self):
        self.booking.lesson_duration = None
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


    def test_valid_lesson_duration(self):
        self.assertTrue(self.booking.lesson_duration == 30 or 
                        self.booking.lesson_duration == 45 or 
                        self.booking.lesson_duration == 60 )

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking.full_clean()