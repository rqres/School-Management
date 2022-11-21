from django.test import TestCase
from lessons.models import User
from django.core.exceptions import ValidationError

# Create your tests here.


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "john.doe@example.org",
            first_name="John",
            last_name="Doe",
            password="TestPassword123",
        )

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_may_already_exist(self):
        User.objects.create_user(
            "jake.smith@example.org",
            first_name="Jake",
            last_name="Smith",
            password="TestPassword123",
        )
        self.user.first_name = "Jake"

        self._assert_user_is_valid()

    def test_first_name_must_not_have_more_than_50_chars(self):
        self.user.first_name = "x" * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_may_already_exist(self):
        User.objects.create_user(
            "jane.lang@example.org",
            first_name="Jane",
            last_name="Lang",
            password="TestPassword123",
        )

        self.user.last_name = "Lang"
        self._assert_user_is_valid()

    def test_last_name_must_not_have_more_than_50_chars(self):
        self.user.last_name = "x" * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ""
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        User.objects.create_user(
            "jane.doe@example.org",
            first_name="Jane",
            last_name="Doe",
            password="TestPassword123",
        )

        self.user.email = "jane.doe@example.org"
        self._assert_user_is_invalid()

    def test_default_user_has_no_flags_set(self):
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_student)
        self.assertFalse(self.user.is_teacher)
        self.assertFalse(self.user.is_parent)

    def test_valid_user(self):
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail("User should be valid")

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
