from django.test import TestCase
from lessons.models import User, Student
from django.core.exceptions import ValidationError

# Create your tests here.


class StudentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "john.doe@example.org",
            first_name="John",
            last_name="Doe",
            password="TestPassword123",
        )

        self.student = Student.objects.create(user=self.user, school_name="Test School")

    def test_corresponding_user_must_not_be_none(self):
        self.student.user = None
        self._assert_student_is_invalid()

    def test_student_is_deleted_when_corresponding_user_is_deleted(self):
        self.student.save()
        before = list(Student.objects.all())
        self.user.delete()
        after = list(Student.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_school_must_not_be_blank(self):
        self.student.school_name = ""
        self._assert_student_is_invalid()

    def test_school_name_cannot_be_over_100_chars(self):
        self.student.school_name = "x" * 101
        self._assert_student_is_invalid()

    def test_school_name_may_already_exist(self):
        same_school_user = User.objects.create_user(
            "jane.doe@example.org",
            first_name="Jane",
            last_name="Doe",
            password="TestPassword123",
        )

        Student.objects.create(user=same_school_user, school_name="School2")
        self.student.school_name = "School2"

        self._assert_student_is_valid()

    def test_valid_student(self):
        self._assert_student_is_valid()

    def _assert_student_is_valid(self):
        try:
            self.student.full_clean()
        except (ValidationError):
            self.fail("Student should be valid")

    def _assert_student_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()
