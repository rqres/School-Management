from datetime import date
import random
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker
from lessons.models import (
    Booking, 
    RequestForLessons,
    SchoolAdmin,
    SchoolTerm,
    Student,
    User,
    Teacher,
)


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker("en_GB")

    def handle(self, *args, **options):
        print("Seeding base users (1 student, 1 admin, 1 director)...")
        self._base_seeder()
        print("Seeding 100 additional students...")
        self._seed_students()
        print("Seeding 20 additional teachers...")
        self._seed_teachers()
        print("Seeding school terms...")
        self._seed_school_terms()
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

            SchoolAdmin.objects.create(
                user=petra,
                school_name="King's College London",
                is_director=False,
                can_create_admins=False,
                can_edit_admins=False,
                can_delete_admins=False,
            )
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
            marty.is_director = True
            marty.save()

            # directors automatically do anything so don't need privileges and hence all have been set to false
            SchoolAdmin.objects.create(
                user=marty,
                is_director=True,
                school_name="King's College London",
                can_create_admins=True,
                can_edit_admins=True,
                can_delete_admins=True,
            )
        except IntegrityError:
            print("     >Director object 'Marty' already exists - skipping...")
        else:
            print("     >Created director marty.major@example.org")

    def _seed_requests(self):
        # create 3 unfulfilled and 3 fulfilled requests
        # for every regular user in the DB
        reg_users = User.objects.filter(is_school_admin=False).filter(is_admin=False)
        for u in reg_users:
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
                    user=u,
                    fulfilled=False,
                    availability=availability,
                    no_of_lessons=no_of_lessons,
                    days_between_lessons=days_between_lessons,
                    lesson_duration=lesson_duration,
                    other_info=other_info,
                )
                # fulfilled request:
                availability = ",".join(random.sample(WEEKDAYS, random.randrange(1, 7)))
                no_of_lessons = random.randrange(2, 40)
                days_between_lessons = random.randrange(2, 14)
                lesson_duration = random.choice((15, 30, 60))
                other_info = self.faker.sentence()
                RequestForLessons.objects.create(
                    user=u,
                    fulfilled=True,
                    availability=availability,
                    no_of_lessons=no_of_lessons,
                    days_between_lessons=days_between_lessons,
                    lesson_duration=lesson_duration,
                    other_info=other_info,
                )
                booking = Booking.objects.create(
                    num_of_lessons=no_of_lessons,
                    user=u,
                    teacher=random.choice(Teacher.objects.all()),
                    description=f'A description about the music lesson',
                    days_between_lessons=days_between_lessons,
                    lesson_duration=lesson_duration,
                )
                booking.save()
                booking.create_lessons()
                print(".", end="", flush=True)

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
            print(".", end="", flush=True)
        print("")

    def _seed_teachers(self):
        for i in range(20):
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
            user.is_teacher = True

            user.save()

            Teacher.objects.create(user=user, school_name=school)
            print(".", end="", flush=True)
        print("")

    def _seed_school_terms(self):
        start_dates = [
            date(2022, 9, 1),
            date(2022, 10, 31),
            date(2023, 1, 3),
            date(2023, 2, 20),
            date(2023, 4, 17),
            date(2023, 6, 5),
        ]
        end_dates = [
            date(2022, 10, 21),
            date(2022, 12, 16),
            date(2023, 2, 10),
            date(2023, 3, 31),
            date(2023, 5, 26),
            date(2023, 7, 21),
        ]

        for (start_date, end_date) in zip(start_dates, end_dates):
            term = SchoolTerm(start_date=start_date, end_date=end_date)
            try:
                term.full_clean()
            except ValidationError:
                print("     >School term already exists or is invalid - skipping...")
            else:
                term.save()
