from datetime import timedelta
from django.core.validators import ValidationError
from django.test import TestCase
from django.utils import timezone

from lessons.models import SchoolTerm


class SchoolTermTestCase(TestCase):
    def setUp(self):
        self.term = SchoolTerm.objects.create(
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=90)
        )

    def test_term_start_date_must_not_be_blank(self):
        self.term.start_date = None
        self._assert_term_is_invalid()

    def test_term_end_date_must_not_be_blank(self):
        self.term.end_date = None
        self._assert_term_is_invalid()

    def test_start_date_cannot_be_greater_than_end_date(self):
        self.term.start_date = self.term.end_date + timedelta(days=10)
        self._assert_term_is_invalid()

    def test_overlapping_term_is_invalid(self):
        other_term = SchoolTerm.objects.create(
            start_date=timezone.now() + timedelta(days=120),
            end_date=timezone.now() + timedelta(days=120) + timedelta(days=90),
        )
        self.term.start_time = other_term.start_date + timedelta(days=30)
        self._assert_term_is_invalid()

    def _assert_term_is_valid(self):
        try:
            self.term.full_clean()
        except (ValidationError):
            self.fail("Term should be valid")

    def _assert_term_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term.full_clean()
