from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import datetime
import random


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, is_active=True):
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
            is_active=True,
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
    """
    Defines a user with first name, last name, email and the type of user they are
    """
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)

    # vvvvvv equivalent of django sysadmin - we can ignore this
    is_admin = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    # child-parent relations (many to many)
    parents = models.ManyToManyField("self")
    children = models.ManyToManyField("self")

    objects = CustomUserManager()

    # THIS TELLS DJANGO TO USE THE EMAIL FIELD AS USERNAME
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        """This allows the user to be defined by their email"""
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
        return self.is_admin or self.is_school_admin


class Student(models.Model):
    """Defines a user to be a student with the given name of the school"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # add extra fields for students here:
    school_name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        """This allows the user to be defined by their email"""
        return self.user.email


class Teacher(models.Model):
    """Defines a user to be a teacher with the given name of the school"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # add extra fields for teachers here:
    school_name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        """This allows the user to be defined by their email"""
        return self.user.email


class SchoolAdmin(models.Model):
    """Defines a user to be a school admin with the given name of the school"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # extra fields for director:
    school_name = models.CharField(max_length=100, blank=False)
    #This sets the school admin to not also be a director by default
    is_director = models.BooleanField(default=False)
    can_create_admins = models.BooleanField(default=False)
    can_edit_admins = models.BooleanField(default=False)
    can_delete_admins = models.BooleanField(default=False)

    def __str__(self):
        """This allows the user to be defined by their email"""
        return self.user.email


class Invoice(models.Model):
    """Defines an invoice with the given user, its unique reference number and price"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    student_num = models.IntegerField(blank=False)
    invoice_num = models.IntegerField(blank=False)
    urn = models.CharField(max_length=50)
    price = MoneyField(decimal_places=2, max_digits=5, default_currency="GBP")
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """creates the unique reference number of the invoice by adding the student number and invoice number"""
        self.student_num = self.user.pk + 1000
        self.urn = str(self.student_num) + "-" + str(self.invoice_num)
        super(Invoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            "student_num",
            "invoice_num",
        )

    def __str__(self):
        """This allows the invoice to be defined by its unique reference number"""
        return self.urn


class Booking(models.Model):
    """Defines a booking with the given number of lessons, days between lessons and lesson duration, an invoice,
    the user the booking is for, the teacher the booking is for and the given description"""
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
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=False)
    description = models.CharField(max_length=50, blank=True)
   
    def save(self, *args, **kwargs):
        self.create_invoice()
        super(Booking, self).save(*args, **kwargs)

    def create_lessons(self):
        """Creates a set of lessons for the confirmed booking"""

        # Generates a random time of the lesson to start
        timeForLesson = random.randint(9, 15)
        startDate = SchoolTerm.objects.first().start_date
        new_date=startDate+datetime.timedelta(days = self.days_between_lessons)
        COUNT = 0
        while COUNT != self.num_of_lessons:
            try:
                lesson = Lesson.objects.create(
                    name=f'{self.user.first_name}{self.teacher.user.first_name}{COUNT}',
                    date=new_date,
                    startTime=datetime.time(timeForLesson, 0, 0),
                    booking=self,
                    description = self.description
                )
                lesson.save()
                COUNT += 1
                new_date+=datetime.timedelta(days = self.days_between_lessons)
            except:
                new_date+=datetime.timedelta(days = self.days_between_lessons)
                continue

    def update_lessons(self):
        """Lessons should be updated depending on the changes made to Booking"""
        self.lesson_set.all().delete()
        self.create_lessons()
        
    def create_invoice(self):
        """Invoice should be created for Lesson that has been created"""
        try:
            if self.invoice is not None:
                pass
        except ObjectDoesNotExist:
            costOfBooking = self.lesson_duration * self.num_of_lessons / 10
            self.invoice = Invoice.objects.create(
                user=self.user,
                student_num=self.user.pk + 1000,
                invoice_num=self.user.invoice_set.all().count() + 1,
                price=Money(costOfBooking, "GBP"),
            )
            self.invoice.save()

    def update_invoice(self):
        """Invoice should be updated depending on the changes made to Lesson"""
        costOfBooking = self.lesson_duration * self.num_of_lessons / 10
        self.invoice.price = Money(costOfBooking, "GBP")


class Lesson(models.Model):
    """Defines a lesson by the given name of the user, date of the lesson, time of the lesson,
    the time this lesson is created and a given description"""
    name = models.CharField(max_length=50, blank=False)
    date = models.DateField(blank=False)
    startTime = models.TimeField(blank=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=False)
    lessonCreatedAt = models.TimeField(auto_now_add=True)
    description = models.CharField(max_length=500, blank=True)

    def clean(self):
        # Check that date is within one of the school terms
        if self.date is not None:
            currentTerm = None
            schoolTerms = SchoolTerm.objects.all()
            for term in schoolTerms:
                if self.date > term.start_date and self.date < term.end_date:
                    currentTerm = term
            if currentTerm is None:
                raise ValidationError("Date of lesson does not lie in the terms")

    class Meta:
        # Model options
        ordering = ["-lessonCreatedAt"]


class RequestForLessons(models.Model):
    """Defines a request with the name of the user, the days that the user is available,
     the number of days between lessons, the desired lesson duration of the user, the time this request is created,
     and other information that was given by the user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # i am storing the availabilty as a comma separated string of days
    # e.g: "TUE,SAT,SUN" = student is available on tuesday saturday and sunday
    # max length is 28 because at most someone could be avlb every day
    # len("MON,TUE,WED,THU,FRI,SAT,SUN") = 27
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
    """Defines school term with the given start date and the given end date"""
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    # vvv i only use this for model validation
    _editing = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_date"]

    def clean(self):
        """Checks if the created school term overlap with one another"""
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be greater than end date")

            # this case applies only when editing a school term
            # I only want to check overlap against visible school terms
            # while editing a term, it will be marked with "editing=True"
            # so as not to check overlapping against itself
            all_terms = SchoolTerm.objects.filter(_editing=False)

            for term in all_terms:
                if (
                    self.start_date <= term.end_date
                    and self.end_date >= term.start_date
                ):
                    raise ValidationError("School terms cannot overlap!")
