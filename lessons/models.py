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
