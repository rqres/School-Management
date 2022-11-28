"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from lessons.forms import PaymentForm
from lessons.models import Invoice, Student, User
from djmoney.money import Money

class PaymentFormTestCase(TestCase):
    """Unit tests of the log in form."""
    def setUp(self):
        self.user_student = User.objects.create_user(
            "john.doe@example.org",
            first_name="John",
            last_name="Doe",
            password="TestPassword123",
        )

        self.user_student.is_student = True

        self.student = Student.objects.create(
            user = self.user_student,
            school_name = "Test School"
        )
        self.invoice = Invoice(
            student_num = self.student.user.pk + 1000,
            invoice_num = Invoice.objects.filter(student_num=self.student.user.pk).count() + 1,
            price = Money(10,'GBP')
        )  
        self.invoice.save() 

        self.form_input = {
            'invoice_urn': '1001-1',
            'account_name' : 'John Doe',
            'account_number' : '12345678',
            'sort_code' : '123456',
            'postcode': 'AB12 3SU'}

    def test_form_contains_required_fields(self):
        form = PaymentForm()
        self.assertIn('invoice_urn', form.fields)
        self.assertIn('account_name', form.fields)
        self.assertIn('account_number', form.fields)
        self.assertIn('sort_code', form.fields)
        self.assertIn('postcode', form.fields)

    def test_valid_request_form(self):
        form = PaymentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_invoice_urn(self):
        self.form_input['invoice_urn'] = ''
        form = PaymentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_account_name(self):
        self.form_input['account_name'] = ''
        form = PaymentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_account_number(self):
        self.form_input['account_number'] = None
        form = PaymentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_sort_code(self):
        self.form_input['sort_code'] = None
        form = PaymentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_post_code(self):
        self.form_input['postcode'] = ''
        form = PaymentForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        
     #TODO: Test for all the validations