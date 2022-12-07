from lessons.models import SchoolTerm, Booking, User, Student, Teacher

class LogInTester:
    def is_logged_in(self):
        return "_auth_user_id" in self.client.session.keys()

fixtures = [
    "lessons/tests/fixtures/default_student.json",
    "lessons/tests/fixtures/default_teacher.json",
]
def create_test_bookings(booking_count):
        user = User.objects.get(email="john.doe@example.org")
        student = Student.objects.get(user=user)

        for booking_id in range(booking_count):
            user_teacher = User.objects.create_user(
                f"teacher{booking_id}@example.org",
                first_name=f"First{booking_id}",
                last_name=f"Last{booking_id}",
                password="TestPassword123",
            )

            user_teacher.is_teacher = True

            new_teacher = Teacher.objects.create(
                user=user_teacher, school_name="Test School"
            )
            booking = Booking.objects.create(
                num_of_lessons = booking_count,
                student = student,
                teacher = new_teacher,
                description = f'Gutitar lesson on basics{booking_id}',
                days_between_lessons = 7,
                lesson_duration = 60,
            )
            booking.create_invoice()
            booking.create_lessons()
            booking.save()
