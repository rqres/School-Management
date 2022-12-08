from django.test import TestCase
from django import forms
from lessons.forms import EditLessonForm
from lessons.models import SchoolTerm, Lesson, Booking, User, Teacher
from djmoney.money import Money
import datetime

class EditBookingFormTestCase(TestCase):
    """Unit tests for editing lesson form"""

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

        self.lesson = Lesson(
            name = f'{self.user.first_name}{self.teacher.user.last_name}Guitar1',
            date = datetime.date(2022,9,10),     
            startTime = datetime.time(11,0,0),
            booking = self.booking,
        )
        self.lesson.save()

        self.form_input = {
            "name": "Name of lesson",
            "date": "2022-10-10",
            "startTime": "10:00",
            "description": "This is the updated lesson.",
        }

    def test_valid_edit_booking_form(self):
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertTrue(form.is_valid())

    def test_form_contains_required_fields(self):
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertIn("name", form.fields)
        self.assertIn("date", form.fields)
        self.assertIn("startTime", form.fields)
        self.assertIn("description", form.fields)
        description_field = form.fields["description"].widget
        self.assertTrue(isinstance(description_field, forms.Textarea))
        date_field = form.fields["date"].widget
        self.assertTrue(isinstance(date_field, forms.DateInput))
        startTime_field = form.fields["startTime"].widget
        self.assertTrue(isinstance(startTime_field, forms.TimeInput))

    def test_form_intially_filled_with_booking_data(self):
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertEqual(
            form.fields["name"].initial, 
            self.lesson.name
        )
        self.assertEqual(
            form.fields["date"].initial,
            self.lesson.date,
        )
        self.assertEqual(
            form.fields["startTime"].initial, 
            self.lesson.startTime
        )
        self.assertEqual(
            form.fields["description"].initial, 
            self.lesson.description
        )
        
    def test_form_rejects_blank_name_field(self):
        self.form_input['name'] = ""
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_blank_date_field(self):
        self.form_input['date'] = None
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_startTime_field(self):
        self.form_input['startTime'] = None
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_description_field(self):
        self.form_input['description'] = None
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        self.assertTrue(form.is_valid())

    def test_form_saves_correctly(self):
        form = EditLessonForm(
            lesson=self.lesson, data=self.form_input
        )
        before_count = Lesson.objects.count()
        lesson = form.save()
        after_count = Lesson.objects.count()
        self.assertEqual(before_count,after_count)
        self.assertEqual(lesson.name,self.form_input['name'])
        self.assertEqual(lesson.date,datetime.date(2022,10,10))
        self.assertEqual(lesson.startTime,datetime.time(10,0,0))
        self.assertEqual(lesson.description,self.form_input['description'])