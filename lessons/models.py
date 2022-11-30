from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Count
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


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


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # extra fields for director:
    school_name = models.CharField(max_length=100, blank=False)


class Invoice(models.Model):
    student_num = models.IntegerField(blank=False)
    invoice_num = models.IntegerField(blank=False)
    urn = models.CharField(max_length=50)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.urn = str(self.student_num) + "-" + str(self.invoice_num)
        super(Invoice, self).save(*args, **kwargs)


class Booking(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=False)
    description = models.CharField(max_length=50, blank=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=False)
    startTime = models.DateTimeField(blank=False)
    endTime = models.DateTimeField(blank=False)
    bookingCreatedAt = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.invoice = Invoice.objects.create(
            student_num=self.student.user.pk + 1000,
            invoice_num=self.student.booking_set.count() + 1,
        )
        self.invoice.save()
        super(Booking, self).save(*args, **kwargs)

    def clean(self):
        if self.startTime is not None and self.endTime is not None:
            duration = self.endTime - self.startTime
            minutes = duration.total_seconds() / 60
            if not (minutes == 30 or minutes == 45 or minutes == 60):
                raise ValidationError(
                    "Length of lesson sholud be 30 or 45 or 60 minutes"
                )

    class Meta:
        # Model options
        ordering = ["-bookingCreatedAt"]

    def __str__(self):
        return (
            f"Booking from {self.startTime.strftime('%H:%M')}"
            f"until {self.endTime.strftime('%H:%M')}."
            " This booking was created at"
            f"{self.bookingCreatedAt.strftime('%H:%M')}"
        )


class RequestForLessons(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # todo: availability field
    # WEEKDAYS = [
    #     ("MON", "Monday"),
    #     ("TUE", "Tuesday"),
    #     ("WED", "Wednesday"),
    #     ("THU", "Thursday"),
    #     ("FRI", "Friday"),
    #     ("SAT", "Saturday"),
    #     ("SUN", "Sunday"), ]
    # availability = models.MultipleChoiceField()
    # availability = models.CharField(max_length=500, blank=True)

    fulfilled = models.BooleanField(default=False)

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

    def __str__(self):
        return f"{self.student}: {self.no_of_lessons} lessons"
