from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Lesson, User , Student , Teacher
from djmoney.money import Money
import datetime

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

        self.lesson = Lesson(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar1',
            description = 'Gutitar lesson on basics',
            startTime = datetime.datetime(2022,11,10,10,0,0),     
            endTime = datetime.datetime(2022,11,10,11,0,0)
        )
        self.lesson.save()
        self.lesson_other = Lesson(
            name = f'{self.student.user.first_name}{self.teacher.user.last_name}Guitar15',
            description = 'Gutitar lesson on basics continued',
            startTime = datetime.datetime(2022,11,11,10,0,0),     
            endTime = datetime.datetime(2022,11,11,11,0,0)
        )
        self.lesson_other.save()

    def test_valid_lesson(self):
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Test lesson should be valid")

    def test_name_field_must_not_be_blank(self):
        self.lesson.name = ''
        self._assert_lesson_is_invalid()

    def test_description_field_must_not_be_blank(self):
        self.lesson.description = ''
        self._assert_lesson_is_invalid()
    
    def test_startTime_field_must_not_be_blank(self):
        self.lesson.startTime = None
        self._assert_lesson_is_invalid()

    def test_endTime_field_must_not_be_blank(self):
        self.lesson.endTime = None
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

    def test_name_field_is_unique(self):
        self.lesson.name = self.lesson_other.name
        self._assert_lesson_is_invalid()


    def test_valid_length_of_lesson(self):
        duration = self.lesson.endTime - self.lesson.startTime
        minutes = duration.total_seconds()/60
        self.assertTrue(minutes == 30 or 
                        minutes == 45 or 
                        minutes == 60 )

    def test_invalid_length_of_lesson(self):
        self.lesson.startTime = datetime.datetime(2022,11,10,11,0,0)
        self.lesson.endTime = datetime.datetime(2022,11,10,10,0,0)
        self._assert_lesson_is_invalid()
    
    def test_invalid_long_length_of_lesson(self):
        self.lesson.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.lesson.endTime = datetime.datetime(2022,11,10,12,0,0)
        self._assert_lesson_is_invalid()

    def test_invalid_short_length_of_lesson(self):
        self.lesson.startTime = datetime.datetime(2022,11,10,10,0,0)
        self.lesson.endTime = datetime.datetime(2022,11,10,10,20,0)
        self._assert_lesson_is_invalid()

    def _assert_lesson_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson.full_clean()