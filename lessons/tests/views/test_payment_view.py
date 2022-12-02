from django.test import TestCase
from django.urls import reverse
from lessons.models import Booking, Invoice, User, Student, Teacher
import datetime
class PaymentFormTest(TestCase):

    fixtures = [
        "lessons/tests/fixtures/default_student.json",
        "lessons/tests/fixtures/default_teacher.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse("payment_form")
        self.user = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user)
        
        self.user_teacher = User.objects.get(email="jane.doe@example.org")
        self.teacher = Teacher.objects.get(user=self.user_teacher)

        self.booking = Booking(
            num_of_lessons = 10,
            student = self.student,
            teacher = self.teacher,
            description = 'Gutitar lesson on basics',
            days_between_lessons = 7,
            lesson_duration = 60,
        )
        self.booking.save()
        self.booking.create_invoice()

        self.data = {
            'invoice_urn': self.booking.invoice.urn,
            'account_name' : 'John Doe',
            'account_number' : '12345678',
            'sort_code' : '123456',
            'postcode': 'AB12 3SU'}


    def test_payment_url(self):
        self.assertEqual(self.url, "/account/payment/")

    def test_new_payment_redirects_when_not_logged_in(self):
        invoice_to_be_paid = Invoice.objects.get(urn = self.data['invoice_urn'])
        self.assertFalse(invoice_to_be_paid.is_paid)
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertFalse(invoice_to_be_paid.is_paid)

    def test_successful_new_payment(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        invoice_to_be_paid = Invoice.objects.get(urn = self.data['invoice_urn'])
        self.assertFalse(invoice_to_be_paid.is_paid)
        response = self.client.post(self.url, self.data, follow=True)
        invoice_to_be_paid = Invoice.objects.get(urn = self.data['invoice_urn'])
        self.assertTrue(invoice_to_be_paid.is_paid)
        response_url = reverse('account')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'account.html')

    def test_unsuccessful_new_payment(self):
        self.client.login(email=self.student.user.email, password="Watermelon123")
        invoice_to_be_paid = Invoice.objects.get(urn = self.data['invoice_urn'])
        self.assertFalse(invoice_to_be_paid.is_paid)
        self.data['account_name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        self.assertFalse(invoice_to_be_paid.is_paid)
        self.assertTemplateUsed(response, 'payment_form.html')