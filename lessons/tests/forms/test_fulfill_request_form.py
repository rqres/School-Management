import datetime
from django.test import TestCase
from django import forms

from lessons.forms import FulfillLessonRequestForm
from lessons.models import Booking, RequestForLessons, SchoolTerm, Teacher, User


# Create your tests here.


class FulfillRequestFormTestCase(TestCase):
    """Unit tests for fulfilling the request for lessons form"""

    fixtures = [
        "lessons/tests/fixtures/default_teacher.json",
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.teacher = Teacher.objects.get(pk=5)
        self.request = RequestForLessons.objects.get(pk=1)
        self.user = User.objects.get(pk=2)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )

        self.form_input = {
            "teacher": self.teacher.pk,
            "num_of_lessons": 14,
            "days_between_lessons": 6,
            "lesson_duration": 30,
            "description": "This is a description",
        }

    # Form accepts valid input
    def test_valid_request_form(self):
        form = FulfillLessonRequestForm(
            lesson_request=self.request, data=self.form_input
        )
        self.assertTrue(form.is_valid())

    # Form has necessary fields
    def test_form_has_necessary_fields(self):
        form = FulfillLessonRequestForm(lesson_request=self.request)
        self.assertIn("teacher", form.fields)
        self.assertIn("num_of_lessons", form.fields)
        self.assertIn("days_between_lessons", form.fields)
        self.assertIn("lesson_duration", form.fields)
        self.assertIn("description", form.fields)
        description_field = form.fields["description"].widget
        self.assertTrue(isinstance(description_field, forms.Textarea))

    def test_fulfill_form_is_prefilled_with_data(self):
        form = FulfillLessonRequestForm(lesson_request=self.request)
        self.assertEqual(
            form.fields["num_of_lessons"].initial, self.request.no_of_lessons
        )
        self.assertEqual(
            form.fields["days_between_lessons"].initial,
            self.request.days_between_lessons,
        )
        self.assertEqual(
            form.fields["lesson_duration"].initial, self.request.lesson_duration
        )

    # No bad input
    def test_form_uses_model_validation(self):
        self.form_input["num_of_lessons"] = "ten"
        self.form_input["days_between_lessons"] = "seven"
        self.form_input["lesson_duration"] = "sixty"
        self.form_input["teacher"] = "teacher"
        form = FulfillLessonRequestForm(
            lesson_request=self.request, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = FulfillLessonRequestForm(
            lesson_request=self.request, data=self.form_input
        )
        before_count = Booking.objects.count()
        booking = form.save()
        after_count = Booking.objects.count()
        self.assertTrue(self.request.fulfilled, True)
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(booking.num_of_lessons, 14)
        self.assertEqual(booking.days_between_lessons, 6)
        self.assertEqual(booking.lesson_duration, 30)
        self.assertEqual(booking.description, "This is a description")
        self.assertEqual(booking.teacher, self.teacher)
        self.assertEqual(booking.user, self.user)
        # todo: assertEqual(booking.invoice, ??)
