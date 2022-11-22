from django.core.validators import ValidationError
from django.test import TestCase

from lessons.models import RequestForLessons, Student


class RequestModelTestCase(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_request.json",
    ]

    def setUp(self):
        self.student = Student.objects.get(email="john.doe@example.org")
        self.post = Post(author=self.user, text="Hi")

    def test_corresponding_student_must_not_be_none(self):
        self.request.student = None
        self._assert_request_is_invalid()

    def test_request_is_deleted_when_corresponding_student_is_deleted(self):
        self.request.save()
        before = list(RequestForLessons.objects.all())
        self.request.student.delete()
        after = list(RequestForLessons.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_post_author_must_not_be_null(self):
        self.post.author = None
        self._assert_post_is_invalid()

    def test_post_is_deleted_when_user_is_deleted(self):
        self.post.save()
        before = list(Post.objects.all())
        self.user.delete()
        after = list(Post.objects.all())
        self.assertEqual(len(before) - 1, len(after))

    def test_created_at_must_correspond_to_current_time(self):
        time_now = datetime.now()
        self.post.save()
        time_post = self.post.created_at.replace(tzinfo=None)
        self.assertAlmostEqual(time_now, time_post, delta=timedelta(seconds=1))

    def _assert_post_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.post.full_clean()
