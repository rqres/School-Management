from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import datetime


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, first name,
        last name and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)
    # ^^^^^^^^ equivalent of our project's school admins - we care about this

    # vvvvvv equivalent of django sysadmin - we can ignore this
    is_admin = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    # THIS TELLS DJANGO TO USE THE EMAIL FIELD AS USERNAME
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # add extra fields for students here:
    school_name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.user.email


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # add extra fields for teachers here:
    school_name = models.CharField(max_length=100, blank=False)


class SchoolAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # extra fields for director:
    school_name = models.CharField(max_length=100, blank=False)
    directorStatus = models.BooleanField(default=False)


class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False)
    student_num = models.IntegerField(blank=False)
    invoice_num = models.IntegerField(blank=False)
    urn = models.CharField(max_length=50)
    price = MoneyField(decimal_places=2, max_digits=5, default_currency="GBP")
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.student_num = self.student.pk + 1000
        self.urn = str(self.student_num) + "-" + str(self.invoice_num)
        super(Invoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            "student_num",
            "invoice_num",
        )


class Booking(models.Model):
    num_of_lessons = models.IntegerField(blank=False)
    days_between_lessons = models.IntegerField(
        default=7,  # default is one week between each lesson
        blank=False,
        validators=[
            MinValueValidator(
                1, message="Number of days between lessons must be greater than 1!"
            )
        ],
    )
    lesson_duration = models.IntegerField(
        default=60,  # default is 1 hour
        blank=False,
        validators=[
            MinValueValidator(15, message="A lesson must be at least 15 minutes")
        ],
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, blank=True, null=True
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=False)
    description = models.CharField(max_length=50, blank=False)

    def create_lessons(self):
        """Creates a set of lessons for the confirmed booking"""
        for lesson_id in range(self.num_of_lessons):
            lesson = Lesson.objects.create(
                name=f"{self.student.user.first_name}{self.teacher.user.first_name}{lesson_id}",
                # These times could potentially cause conflict with student's schedule
                # TODO: Validate these times
                startTime=datetime.datetime(2022, 11, 10, 10, 0, 0),
                endTime=datetime.datetime(2022, 11, 10, 11, 0, 0),
                booking=self,
            )
            lesson.save()

    def update_lessons(self):
        """Lessons should be updated depending on the changes made to Booking"""
        lessons = self.lesson_set.all()
        # for each on lessons and update each of them
        for lesson in lessons:
            pass

    def create_invoice(self):
        """Invoice should be created for Lesson that has been created"""
        costOfBooking = self.lesson_duration / 10
        self.invoice = Invoice.objects.create(
            student=self.student,
            student_num=self.student.user.pk + 1000,
            invoice_num=self.student.invoice_set.all().count() + 1,
            price=Money(costOfBooking, "GBP"),
        )
        self.invoice.save()

    def update_invoice(self):
        """Invoice should be updated depending on the changes made to Lesson"""
        costOfBooking = self.lesson_duration / 10
        self.invoice.price = Money(costOfBooking, "GBP")


class Lesson(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    startTime = models.DateTimeField(blank=False)
    endTime = models.DateTimeField(blank=False)
    duration = models.IntegerField(blank=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=False)
    lessonCreatedAt = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.duration = (self.endTime - self.startTime).total_seconds()
        super(Lesson, self).save(*args, **kwargs)

    def clean(self):
        if self.startTime is not None and self.endTime is not None:
            duration = self.endTime - self.startTime
            minutes = round(duration.total_seconds() / 60)
            if not (minutes == 30 or minutes == 45 or minutes == 60):
                raise ValidationError(
                    "Length of lesson should be 30 or 45 or 60 minutes"
                )

    class Meta:
        # Model options
        ordering = ["-lessonCreatedAt"]

    def __str__(self):
        return (
            f"Booking from {self.startTime.strftime('%H:%M')}"
            f"until {self.endTime.strftime('%H:%M')}."
            " This booking was created at"
            f"{self.lessonCreatedAt.strftime('%H:%M')}"
        )


class RequestForLessons(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # i am storing the availabilty as a comma separated string of days
    # e.g: "tue,sat,sun" = student is available on tuesday saturday and sunday
    # max length is 28 because at most someone could be avlb every day
    # len("mon,tue,wed,thu,fri,sat,sun") = 27
    availability = models.CharField(max_length=27, blank=False)

    fulfilled = models.BooleanField(default=False)
    request_created_at = models.DateTimeField(auto_now_add=True, blank=False)

    no_of_lessons = models.IntegerField(
        default=10,  # default is 10 lessons (per year?)
        blank=False,
        validators=[
            MinValueValidator(1, message="Number of lessons must be greater than 1!")
        ],
    )
    days_between_lessons = models.IntegerField(
        default=7,  # default is one week between each lesson
        blank=False,
        validators=[
            MinValueValidator(
                1, message="Number of days between lessons must be greater than 1!"
            )
        ],
    )
    lesson_duration = models.IntegerField(
        default=60,  # default is 1 hour
        blank=False,
        validators=[
            MinValueValidator(15, message="A lesson must be at least 15 minutes")
        ],
    )
    other_info = models.CharField(max_length=500, blank=True)

    class Meta:
        # Model options
        ordering = ["-request_created_at"]

    def __str__(self):
        return f"{self.student}: {self.no_of_lessons} lessons"

    def clean(self):
        valid_days = ["", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        availability_list = self.availability.split(",")
        for day in availability_list:
            if day not in valid_days:
                raise ValidationError(
                    "Availability list must only contain days of the week (the first 3 letters in capitals)"
                )


class SchoolTerm(models.Model):
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    class Meta:
        ordering = ["-start_date"]

    def clean(self):
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be greater than end date")

            all_terms = SchoolTerm.objects.all()
            for term in all_terms:
                if (
                    self.start_date >= term.start_date
                    and self.start_date <= term.end_date
                ) or (
                    self.end_date <= term.end_date and self.end_date >= term.start_date
                ):
                    raise ValidationError("School terms cannot overlap!")
