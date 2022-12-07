from django.core.validators import ValidationError
from django.test import TestCase

from lessons.models import RequestForLessons, Student, User


class RequestModelTestCase(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.request = self.user.requestforlessons_set.first()

    def test_corresponding_student_must_not_be_none(self):
        self.request.user = None
        self._assert_request_is_invalid()

    def test_request_is_deleted_when_corresponding_student_is_deleted(self):
        before = list(RequestForLessons.objects.all())
        self.request.user.delete()
        after = list(RequestForLessons.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_request_is_unfulfilled_by_default(self):
        self.assertFalse(self.request.fulfilled)

    def test_availability_cannot_be_blank(self):
        self.request.availability = ""
        self._assert_request_is_invalid()

    def test_availability_must_not_contain_invalid_days(self):
        self.request.availability += ",BAD"
        self._assert_request_is_invalid()

    def test_availability_may_have_27_chars(self):
        self.request.availability = "MON,TUE,WED,THU,FRI,SAT,SUN"
        self._assert_request_is_valid()

    def test_availability_cannot_be_over_27_chars(self):
        self.request.availability = "MON,TUE,WED,THU,FRI,SAT,SUN,"
        self._assert_request_is_invalid()

    def test_no_of_lessons_cannot_be_blank(self):
        self.request.no_of_lessons = ""
        self._assert_request_is_invalid()

    def test_days_between_lessons_cannot_be_blank(self):
        self.request.days_between_lessons = ""
        self._assert_request_is_invalid()

    def test_lesson_duration_cannot_be_blank(self):
        self.request.lesson_duration = ""
        self._assert_request_is_invalid()

    def test_no_of_lessons_must_be_greater_than_1(self):
        self.request.no_of_lessons = 0
        self._assert_request_is_invalid()

    def test_days_between_lessons_must_be_greater_than_1(self):
        self.request.days_between_lessons = 0
        self._assert_request_is_invalid()

    def test_lesson_duration_must_be_greater_than_1(self):
        self.request.lesson_duration = 0
        self._assert_request_is_invalid()

    def test_other_info_cannot_be_over_500_chars(self):
        self.request.other_info = "x" * 501
        self._assert_request_is_invalid()

    def test_other_info_may_have_500_chars(self):
        self.request.other_info = "x" * 500
        self._assert_request_is_valid()

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except (ValidationError):
            self.fail("Request should be valid")

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
