from django.db import IntegrityError
from django.test import TestCase
from django import forms

from lessons.forms import RequestForLessonsForm
from lessons.models import RequestForLessons, Student , User


# Create your tests here.


class RequestForLessonsFormTestCase(TestCase):
    """Unit tests for the request for lessons form"""

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
    ]

    def setUp(self):
        self.form_input = {
            "no_of_lessons": 10,
            "days_between_lessons": 7,
            "lesson_duration": 60,
            "other_info": "This is some info",
        }

    # Form accepts valid input
    def test_valid_request_form(self):
        form = RequestForLessonsForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Form has necessary fields
    def test_form_has_necessary_fields(self):
        form = RequestForLessonsForm()
        self.assertIn("no_of_lessons", form.fields)
        self.assertIn("days_between_lessons", form.fields)
        self.assertIn("lesson_duration", form.fields)
        self.assertIn("other_info", form.fields)
        other_info_field = form.fields["other_info"].widget
        self.assertTrue(isinstance(other_info_field, forms.Textarea))

    # No bad input
    def test_form_uses_model_validation(self):
        self.form_input["no_of_lessons"] = "ten"
        self.form_input["days_between_lessons"] = "seven"
        self.form_input["lesson_duration"] = "sixty"
        form = RequestForLessonsForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_cannot_be_submitted_without_a_student_object(self):
        with self.assertRaises(IntegrityError):
            form = RequestForLessonsForm(data=self.form_input)
            form.save()
            form.delete()

    def test_form_must_save_correctly(self):
        user = User.objects.get(email="john.doe@example.org")
        student = Student.objects.get(user=user)
        form = RequestForLessonsForm(student=student, data=self.form_input)
        before_count = RequestForLessons.objects.count()
        request = form.save()
        after_count = RequestForLessons.objects.count()
        self.assertEqual(after_count, before_count + 1)
        # request = RequestForLessons.objects.get()
        self.assertEqual(request.no_of_lessons, 10)
        self.assertEqual(request.days_between_lessons, 7)
        self.assertEqual(request.lesson_duration, 60)
        self.assertEqual(request.other_info, "This is some info")
