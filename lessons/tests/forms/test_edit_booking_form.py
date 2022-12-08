from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from lessons.forms import EditBookingForm
from lessons.models import SchoolTerm, Booking, User, Teacher
from djmoney.money import Money
import datetime

class EditBookingFormTestCase(TestCase):
    """Unit tests for editing booking form"""

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]
    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.teacher = Teacher.objects.get(pk=5)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )
        self.booking = Booking(
            num_of_lessons=10,
            user=self.user,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            days_between_lessons=7,
            lesson_duration=60,
        )
        self.booking.save()

        self.form_input = {
            "teacher": self.teacher,
            "num_of_lessons": 14,
            "days_between_lessons": 7,
            "lesson_duration": 60,
            "description": "Edited booking"
        }

    def test_valid_edit_booking_form(self):
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertTrue(form.is_valid())

    def test_form_contains_required_fields(self):
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertIn("teacher", form.fields)
        self.assertIn("num_of_lessons", form.fields)
        self.assertIn("days_between_lessons", form.fields)
        self.assertIn("lesson_duration", form.fields)
        self.assertIn("description", form.fields)
        description_field = form.fields["description"].widget
        self.assertTrue(isinstance(description_field, forms.Textarea))

    def test_form_intially_filled_with_booking_data(self):
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertEqual(
            form.fields["num_of_lessons"].initial, 
            self.booking.num_of_lessons
        )
        self.assertEqual(
            form.fields["days_between_lessons"].initial,
            self.booking.days_between_lessons,
        )
        self.assertEqual(
            form.fields["lesson_duration"].initial, 
            self.booking.lesson_duration
        )
        self.assertEqual(
            form.fields["teacher"].initial, 
            self.booking.teacher
        )
        self.assertEqual(
            form.fields["description"].initial, 
            self.booking.description
        )
    def test_form_rejects_blank_teacher_field(self):
        self.form_input['teacher'] = None
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_blank_num_of_lessons_field(self):
        self.form_input['num_of_lessons'] = None
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_days_between_lessons_field(self):
        self.form_input['days_between_lessons'] = None
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_lesson_duration_field(self):
        self.form_input['lesson_duration'] = None
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_description_field(self):
        self.form_input['description'] = None
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        self.assertTrue(form.is_valid())

    def test_form_saves_correctly(self):
        form = EditBookingForm(
            booking=self.booking, data=self.form_input
        )
        before_count = Booking.objects.count()
        booking = form.save()
        after_count = Booking.objects.count()
        self.assertEqual(before_count,after_count)
        self.assertEqual(booking.teacher,self.form_input['teacher'])
        self.assertEqual(booking.num_of_lessons,self.form_input['num_of_lessons'])
        self.assertEqual(booking.days_between_lessons,self.form_input['days_between_lessons'])