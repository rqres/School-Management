from django.test import TestCase
from lessons.models import Student, User
from django.core.exceptions import ValidationError

# Create your tests here.


class StudentModelTestCase(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/other_students.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)

    def test_corresponding_user_must_not_be_none(self):
        self.student.user = None
        self._assert_student_is_invalid()

    def test_student_is_deleted_when_corresponding_user_is_deleted(self):
        # self.student.save()
        before = list(Student.objects.all())
        self.student.user.delete()
        after = list(Student.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_school_must_not_be_blank(self):
        self.student.school_name = ""
        self._assert_student_is_invalid()

    def test_school_name_cannot_be_over_100_chars(self):
        self.student.school_name = "x" * 101
        self._assert_student_is_invalid()

    def test_school_name_may_already_exist(self):
        other_user = User.objects.get(email="jake.walker@example.org")
        other_student = Student.objects.get(user=other_user)
        self.student.school_name = other_student.school_name

        self._assert_student_is_valid()

    def test_student_has_only_student_flag_set(self):
        self.assertTrue(self.student.user.is_student)
        self.assertFalse(self.student.user.is_admin)
        self.assertFalse(self.student.user.is_teacher)
        self.assertFalse(self.student.user.is_parent)

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
