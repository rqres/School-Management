from datetime import date
from django.db import IntegrityError
from django.test import TestCase
from django import forms

from lessons.forms import RequestForLessonsForm, SchoolTermForm
from lessons.models import SchoolTerm, Student, User


# Create your tests here.


class SchoolTermFormTestCase(TestCase):
    """Unit tests for the request for lessons form"""

    def setUp(self):
        self.form_input = {"start_date": "2022-10-10", "end_date": "2022-12-14"}

    # Form accepts valid input
    def test_valid_request_form(self):
        form = SchoolTermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Form has necessary fields
    def test_form_has_necessary_fields(self):
        form = SchoolTermForm()
        self.assertIn("start_date", form.fields)
        self.assertIn("end_date", form.fields)

    # No bad input
    def test_form_uses_date_format_validation(self):
        self.form_input["start_date"] = "bad"
        self.form_input["end_date"] = "input"
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_doesnt_accept_start_date_greater_than_end_date(self):
        self.form_input["start_date"], self.form_input["end_date"] = (
            self.form_input["end_date"],
            self.form_input["start_date"],
        )
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_doesnt_accept_overlapping_terms(self):
        SchoolTerm.objects.create(
            start_date=date(2022, 9, 1), end_date=date(2022, 10, 1)
        )
        self.form_input["start_date"] = "2022-08-01"
        self.form_input["end_date"] = "2022-09-25"

        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input["start_date"] = "2022-09-17"
        self.form_input["end_date"] = "2022-12-01"

        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input["start_date"] = "2022-09-17"
        self.form_input["end_date"] = "2022-09-29"

        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input["start_date"] = "2022-06-01"
        self.form_input["end_date"] = "2022-12-01"

        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SchoolTermForm(data=self.form_input)
        before_count = SchoolTerm.objects.count()
        term = form.save()
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(term.start_date, date(2022, 10, 10))
        self.assertEqual(term.end_date, date(2022, 12, 14))
