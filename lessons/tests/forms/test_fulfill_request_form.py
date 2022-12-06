"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from lessons.forms import FulfillLessonRequestForm
from lessons.models import Booking, Invoice, Teacher, Student, User
from djmoney.money import Money


class FulfilLessonRequestTestCase(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]
    """Unit tests of the Fulfil Lesson Request form."""

    def setUp(self):
        self.user_student = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user_student)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)
