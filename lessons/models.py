from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

# # Create your models here.

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
        Creates and saves a superuser with the given email, date of
        birth and password.
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
    # TODO: implement later
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    # TODO: are we calling them admins? directors? superadmins? superusers? idk
    # is_director = models.BooleanField(default=False)
    # for now, im calling them adming as per django docs
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

class Director(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # extra fields for director:

class Invoice(models.Model):
    # TODO:implement invoice with unique reference number
    urn = models.CharField(max_length=50, blank=False)

class Booking(models.Model):
    # Have access to Request model 
    # Each booking has an invoice attached to it 
    student = models.ForeignKey(Student, on_delete=models.CASCADE,blank=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,blank=False)    
    startTime = models.DateTimeField(blank=False)
    endTime = models.DateTimeField(blank=False)
    bookingCreatedAt = models.TimeField(auto_now_add=True)
    # Add description of booking field

    def clean(self):
        if (self.startTime is not None and self.endTime is not None):
            duration = self.endTime - self.startTime
            minutes = duration.total_seconds()/60
            if not(minutes == 30 or minutes == 45 or minutes == 60):
                raise ValidationError('Length of lesson sholud be 30 or 45 or 60 minutes')
    class Meta:
        #Model options
        ordering  = ['-bookingCreatedAt']
    
