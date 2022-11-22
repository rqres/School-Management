from django.test import TestCase
from lessons.models import User
from django.core.exceptions import ValidationError

# Create your tests here.


class UserModelTestCase(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_may_already_exist(self):
        other_user = User.objects.get(email="jake.walker@example.org")
        self.user.first_name = other_user.first_name

        self._assert_user_is_valid()

    def test_first_name_must_not_have_more_than_50_chars(self):
        self.user.first_name = "x" * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_may_already_exist(self):
        other_user = User.objects.get(email="jake.walker@example.org")
        self.user.last_name = other_user.last_name

        self._assert_user_is_valid()

    def test_last_name_must_not_have_more_than_50_chars(self):
        self.user.last_name = "x" * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ""
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        other_user = User.objects.get(email="jake.walker@example.org")

        self.user.email = other_user.email
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
