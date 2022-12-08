from django.test import TestCase
from lessons.models import SchoolAdmin, User
from django.core.exceptions import ValidationError

# Create your tests here.


class SchoolAdminModelTestCase(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="bob.dylan@example.org")
        self.schooladmin = SchoolAdmin.objects.get(
            user=self.user,
        )

    def test_corresponding_user_must_not_be_none(self):
        self.schooladmin.user = None
        self._assert_schooladmin_is_invalid()

    def test_schooladmin_is_deleted_when_corresponding_user_is_deleted(self):
        # self.student.save()
        before = list(SchoolAdmin.objects.all())
        self.schooladmin.user.delete()
        after = list(SchoolAdmin.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_school_must_not_be_blank(self):
        self.schooladmin.school_name = ""
        self._assert_schooladmin_is_invalid()

    def test_school_name_cannot_be_over_100_chars(self):
        self.schooladmin.school_name = "x" * 101
        self._assert_schooladmin_is_invalid()

    def test_all_privileges_can_be_false(self):
        self.schooladmin.directorStatus=False
        self.schooladmin.can_edit_admins = False
        self.schooladmin.can_delete_admins = False
        self.schooladmin.can_create_admins = False
        self._assert_schooladmin_is_valid()

    def test_all_privileges_can_be_true(self):
        self.schooladmin.directorStatus=True
        self.schooladmin.can_edit_admins = True
        self.schooladmin.can_delete_admins = True
        self.schooladmin.can_create_admins = True
        self._assert_schooladmin_is_valid()

    def test_schooladmin_has_only_schooladmin_flag_set(self):
        self.assertFalse(self.schooladmin.user.is_student)
        self.assertTrue(self.schooladmin.user.is_school_admin)
        self.assertFalse(self.schooladmin.user.is_teacher)
        self.assertFalse(self.schooladmin.user.is_parent)

    def test_valid_schooladmin(self):
        self._assert_schooladmin_is_valid()

    def _assert_schooladmin_is_valid(self):
        try:
            self.schooladmin.full_clean()
        except (ValidationError):
            self.fail("SchoolAdmin should be valid")

    def _assert_schooladmin_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.schooladmin.full_clean()
