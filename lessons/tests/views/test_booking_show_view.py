from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolAdmin, SchoolTerm, Lesson, Booking, User, Student, Teacher
from lessons.tests.helpers import create_test_bookings
import datetime


class BookingShowTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_user.json",
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
        "lessons/tests/fixtures/default_director.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(pk=2)

        self.user_student = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user_student)

        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        self.user_director = User.objects.get(email="bob.dylan@example.org")
        self.director = SchoolAdmin.objects.get(user=self.user_director)

        SchoolTerm.objects.create(
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 10, 21),
        )

        #Creates 10 bookings for the above student user
        create_test_bookings(10)

        self.booking_for_other_user = Booking(
            num_of_lessons=10,
            user=self.user,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            days_between_lessons=7,
            lesson_duration=60,
        )
        self.booking_for_other_user.save()

        self.booking_to_show = self.user_student.booking_set.first()

        self.url = reverse(
            "show_booking", kwargs={"booking_id": self.booking_to_show.id}
        )

    def test_show_booking_url(self):
        self.assertEqual(self.url, "/account/bookings/1/")

    def test_show_booking_redirects_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "/log_in/?next=/account/bookings/1/"
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_show_booking_as_a_user(self):
        """ Shows lessons in booking only if the user's booking """
        self.client.login(email=self.student.user.email, password="Watermelon123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,"show_booking.html")
        self.assertNotContains(response,"Edit Lesson") # Edit button


    def test_show_booking_displays_correctly_as_a_director(self):
        self.client.login(email=self.director.user.email, password="Watermelon123")
        lessons_in_booking = Lesson.objects.filter(booking=self.booking_to_show)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,"show_booking.html")
        self.assertContains(response,"Edit Lesson") # Edit button
        for lesson in lessons_in_booking:
            self.assertContains(response, f'{lesson.date.day}, {lesson.date.year}')
            if lesson.startTime.hour > 12:
                self.assertContains(response, f'{lesson.startTime.hour-12} p.m.')
            else:
                self.assertContains(response, f'{lesson.startTime.hour} a.m.')
 
   