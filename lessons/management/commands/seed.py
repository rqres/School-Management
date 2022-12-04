import random
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker
from lessons.models import RequestForLessons, SchoolAdmin, Student, User


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker("en_GB")

    def handle(self, *args, **options):
        print("Seeding base users (1 student, 1 admin, 1 director)...")
        self._base_seeder()
        print("Seeding 100 additional students...")
        self._seed_students()
        print("Seeding requests for lessons...")
        self._seed_requests()

    def _base_seeder(self):
        # create the 3 accounts mentioned in the handbook

        # create student object
        try:
            john = User.objects.create_user(
                "john.doe@example.org",
                first_name="John",
                last_name="Doe",
                password="Password123",
            )
            john.is_student = True

            john.save()

            Student.objects.create(user=john, school_name="King's College London")
        except IntegrityError:
            print("     >Student object 'John' already exists - skipping...")
        else:
            print("     >Created student john.doe@example.org")

        # create admin object
        try:
            petra = User.objects.create_user(
                "petra.pickles@example.org",
                first_name="Petra",
                last_name="Pickles",
                password="Password123",
            )
            petra.is_school_admin = True
            petra.save()

            SchoolAdmin.objects.create(user=petra, school_name="King's College London")
        except IntegrityError:
            print("     >School admin object 'Petra' already exists - skipping...")
        else:
            print("     >Created school admin petra.pickles@example.org")

        # create director object
        try:
            marty = User.objects.create_user(
                "marty.major@example.org",
                first_name="Marty",
                last_name="Major",
                password="Password123",
            )
            marty.is_school_admin = True
            marty.save()

            SchoolAdmin.objects.create(
                user=marty, directorStatus=True, school_name="King's College London"
            )
        except IntegrityError:
            print("     >Director object 'Marty' already exists - skipping...")
        else:
            print("     >Created director marty.major@example.org")

    def _seed_requests(self):
        # create 3 unfulfilled and 3 fulfilled requests
        # for every student in the DB
        for st in Student.objects.all():
            for _ in range(3):
                WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                # unfulfilled request:
                availability = ",".join(
                    # this line chooses a random number (1 to 7) of
                    # random unique days
                    random.sample(WEEKDAYS, random.randrange(1, 7))
                )
                no_of_lessons = random.randrange(2, 40)
                days_between_lessons = random.randrange(2, 14)
                lesson_duration = random.choice((15, 30, 60))
                other_info = self.faker.sentence()
                RequestForLessons.objects.create(
                    student=st,
                    fulfilled=False,
                    availability=availability,
                    no_of_lessons=no_of_lessons,
                    days_between_lessons=days_between_lessons,
                    lesson_duration=lesson_duration,
                    other_info=other_info,
                )
                # fulfilled request:
                availability = ",".join(
                    random.sample(WEEKDAYS, random.randrange(1, 7))
                )
                no_of_lessons = random.randrange(2, 40)
                days_between_lessons = random.randrange(2, 14)
                lesson_duration = random.choice((15, 30, 60))
                other_info = self.faker.sentence()
                RequestForLessons.objects.create(
                    student=st,
                    fulfilled=True,
                    availability=availability,
                    no_of_lessons=no_of_lessons,
                    days_between_lessons=days_between_lessons,
                    lesson_duration=lesson_duration,
                    other_info=other_info,
                )

    def _seed_students(self):
        for i in range(101):
            fname = self.faker.first_name()
            lname = self.faker.last_name()

            school_names = [
                "Imperial",
                "King's",
                "Oxford",
                "Cambridge",
                "Gummies",
                "Sesame",
                "Jelly",
            ]

            school = random.choice(school_names) + "School"
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
