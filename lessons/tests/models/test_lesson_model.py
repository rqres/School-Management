from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import SchoolTerm, Booking, Lesson, User, Student, Teacher
from djmoney.money import Money
import datetime
from datetime import timedelta

class LessonTest(TestCase):
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
            num_of_lessons=10,
            student=self.student,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            days_between_lessons=7,
            lesson_duration=60,
        )
        self.booking.save()

        self.lesson = Lesson(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar1',
            date = datetime.date(2022,9,10),     
            startTime = datetime.time(10,0,0),
            booking = self.booking,
        )
        self.lesson.save()

        self.lesson_other = Lesson(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar15',
            date = datetime.date(2022,10,14),     
            startTime = datetime.time(10,0,0),
            booking = self.booking,
        )
        self.lesson_other.save()

        SchoolTerm.objects.create(
            start_date=datetime.date(2022,9,1),
            end_date=datetime.date(2022,10,21),
        )

    def test_valid_lesson(self):
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Test lesson should be valid")

    def test_name_field_must_not_be_blank(self):
        self.lesson.name = ''
        self._assert_lesson_is_invalid()

    def test_startTime_field_must_not_be_blank(self):
        self.lesson.startTime = None
        self._assert_lesson_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.lesson.name = 'x' * 50
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Test lesson should be valids")

    def test_name_cannot_be_over_50_characters_long(self):
        self.lesson.name = 'x' * 51
        self._assert_lesson_is_invalid()

    def test_startDate_increaces_accordingly(self):
        startDate = SchoolTerm.objects.first().start_date
        self.lesson.date = startDate + timedelta(days=2)
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Test lesson should be valids")

    def _assert_lesson_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson.full_clean()