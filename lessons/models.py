from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

class Student(AbstractUser):
    first_name = models.CharField(max_length= 50, blank = False)
    last_name = models.CharField(max_length= 50, blank = False)
    email = models.EmailField(unique = True)
    school_name = models.CharField(max_length= 200)
    user_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

class Invoice(models.Model):
    # TODO:implement invoice with unique reference number
    pass
class Booking(models.Model):
    # Have access to Request model 
    # Each booking has an invoice attached to it 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)    
    timePeriod = models.TimeField()
    bookingCreatedAt = models.TimeField(auto_created=True)