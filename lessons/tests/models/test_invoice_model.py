from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Invoice, Student, User
from djmoney.money import Money


class InvoiceTest(TestCase):
    fixtures = [
        "lessons/tests/fixtures/default_student.json",
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_student = User.objects.get(email="john.doe@example.org")
        self.student = Student.objects.get(user=self.user_student)

        self.invoice = Invoice(
            user=self.user_student,
            student_num=self.student.user.pk + 1000,
            invoice_num=Invoice.objects.filter(student_num=self.student.user.pk).count()
            + 1,
            price=Money(10, "GBP"),
        )
        self.invoice.save()

        self.second_invoice = Invoice.objects.create(
            user=self.user_student,
            student_num=self.student.user.pk + 1000,
            invoice_num=Invoice.objects.filter(
                student_num=self.invoice.student_num
            ).count()
            + 1,
            price=Money(10, "GBP"),
        )
        self.second_invoice.save()

    def test_valid_invoice(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("Test invoice should be valids")

    def test_student_num_field_must_not_be_blank(self):
        self.invoice.student_num = None
        self._assert_invoice_is_invalid()

    def test_invoice_num_field_must_not_be_blank(self):
        self.invoice.invoice_num = None
        self._assert_invoice_is_invalid()

    def test_urn_field_must_not_be_blank(self):
        self.invoice.urn = None
        self._assert_invoice_is_invalid()

    def test_price_field_must_not_be_blank(self):
        self.invoice.price = None
        self._assert_invoice_is_invalid()

    def test_is_paid_field_is_default_false(self):
        self.assertFalse(self.invoice.is_paid)

    def test_student_num_field_is_valid(self):
        test_user = User.objects.get(pk=int(self.invoice.student_num - 1000))
        try:
            test_user.full_clean()
        except ValidationError:
            self.fail("Invalid student number assigned")

    def test_student_must_have_unique_invoice_nums(self):
        self.invoice.invoice_num = self.second_invoice.invoice_num
        self._assert_invoice_is_invalid()

    def test_urn_contains_valid_student_num(self):
        self.assertIn(str(self.invoice.student_num), self.invoice.urn)

    def test_urn_contains_valid_invoice_num(self):
        self.assertIn(str(self.invoice.invoice_num), self.invoice.urn)

    def test_price_cannot_be_more_than_5_digits(self):
        self.invoice.price = Money(999999, "GBP")
        self._assert_invoice_is_invalid()

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
