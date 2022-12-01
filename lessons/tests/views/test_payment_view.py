from django.test import TestCase
from django.urls import reverse
from lessons.models import Booking, Invoice, User, Student, Teacher
import datetime
from django.utils import timezone


class PaymentFormTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_user.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse("payment_form")
        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)

        # TODO: Create teacher and booking fixtures
        self.user_teacher = User.objects.create_user(
            "jane.dave@example.org",
            first_name="Jane",
            last_name="Dave",
            password="TestPassword123",
        )

        self.user_teacher.is_teacher = True

        self.teacher = Teacher.objects.create(
            user=self.user_teacher, school_name="Test School"
        )

        self.booking = Booking(
            name=f"{self.student.user.first_name}{self.teacher.user.last_name}Guitar1",
            student=self.student,
            teacher=self.teacher,
            description="Gutitar lesson on basics",
            startTime=timezone.now(),
            endTime=timezone.now() + datetime.timedelta(hours=1),
        )
        self.booking.save()

        self.data = {
            "invoice_urn": self.booking.invoice.urn,
            "account_name": "John Doe",
            "account_number": "12345678",
            "sort_code": "123456",
            "postcode": "AB12 3SU",
        }

    def test_payment_url(self):
        self.assertEqual(self.url, "/account/payment/")

    def test_new_payment_redirects_when_not_logged_in(self):
        invoice_to_be_paid = Invoice.objects.get(urn=self.data["invoice_urn"])
        self.assertFalse(invoice_to_be_paid.is_paid)
        redirect_url = reverse("log_in")
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertFalse(invoice_to_be_paid.is_paid)

    def test_successful_new_payment(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        invoice_to_be_paid = Invoice.objects.get(urn=self.data["invoice_urn"])
        self.assertFalse(invoice_to_be_paid.is_paid)
        response = self.client.post(self.url, self.data, follow=True)
        invoice_to_be_paid = Invoice.objects.get(urn=self.data["invoice_urn"])
        self.assertTrue(invoice_to_be_paid.is_paid)
        response_url = reverse("account")
        self.assertRedirects(
            response,
            response_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertTemplateUsed(response, "account.html")

    def test_unsuccessful_new_payment(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        invoice_to_be_paid = Invoice.objects.get(urn=self.data["invoice_urn"])
        self.assertFalse(invoice_to_be_paid.is_paid)
        self.data["account_name"] = ""
        response = self.client.post(self.url, self.data, follow=True)
        self.assertFalse(invoice_to_be_paid.is_paid)
        self.assertTemplateUsed(response, "payment_form.html")
