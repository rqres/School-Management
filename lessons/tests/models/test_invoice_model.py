from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Invoice, Student, User

class InvoiceTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
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
            invoice_num = Invoice.objects.filter(student_num=self.student.user.pk).count() + 1
        )  
        self.invoice.save()

        self.second_invoice = Invoice.objects.create(
            student_num = self.student.user.pk + 1000,
            invoice_num = Invoice.objects.filter(student_num=self.student.user.pk).count() + 1
        )
        self.second_invoice.save()

    def test_valid_invoice(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("Test invoice should be valids")


    def test_student_num_field_must_not_be_blank(self):
        self.invoice.student_num = None
        self._assert_booking_is_invalid()

    def test_invoice_num_field_must_not_be_blank(self):
        self.invoice.invoice_num = None
        self._assert_booking_is_invalid()
    
    def test_student_num_field_is_valid(self):
        test_user = User.objects.get(pk=int(self.invoice.student_num - 1000))
        student = Student.objects.get(user = test_user)
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail('Invalid student number assigned')


    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
    

    