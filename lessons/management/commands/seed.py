import random
from django.core.management.base import BaseCommand
from faker import Faker
from lessons.models import RequestForLessons, Student, User, SchoolAdmin


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker("en_GB")

    def handle(self, *args, **options):
        self._seed_students()
        self._seed_requests()

    def _seed_requests(self):
        # create 3 requests for every student in the DB
        for st in Student.objects.all():
            for _i in range(3):
                RequestForLessons.objects.create(student=st)

    def _seed_students(self):
        for i in range(51):
            fname = self.faker.first_name()
            lname = self.faker.last_name()

            school_names = [
                "danish",
                "cheesecake",
                "sugar",
                "Lollipop",
                "wafer",
                "Gummies",
                "sesame",
                "Jelly",
                "beans",
                "pie",
                "bar",
                "Ice",
                "oat",
            ]

            school = random.choice(school_names) + "School"

            # uname = "@" + fname.lower() + lname.lower()
            email = fname.lower() + "." + lname.lower() + str(i) + "@example.com"

            user = User.objects.create_user(
                email,
                first_name=fname,
                last_name=lname,
                password=(self.faker.password()),
            )
            user.is_student = True

            user.save()

            Student.objects.create(user=user, school_name=school)

        def _seed_directors(self):
            for i in range(10):
                fname = self.faker.first_name()
                lname = self.faker.last_name()

                school_names = [
                    "danish",
                    "cheesecake",
                    "sugar",
                    "Lollipop",
                    "wafer",
                    "Gummies",
                    "sesame",
                    "Jelly",
                    "beans",
                    "pie",
                    "bar",
                    "Ice",
                    "oat",
                ]

                school = random.choice(school_names) + "School"

                # uname = "@" + fname.lower() + lname.lower()
                email = fname.lower() + "." + lname.lower() + str(i) + "@fox.org"

                user = User.objects.create_user(
                email,
                first_name=fname,
                last_name=lname,
                password=(self.faker.password()),
                )
                user.is_school_admin = True

                user.save()

                SchoolAdmin.objects.create(user=user, school_name=school, directorStatus=True)
