from django.core.management.base import BaseCommand
from lessons.models import Booking, RequestForLessons, SchoolTerm, User


class Command(BaseCommand):
    def handle(self, *args, **options):

        regular_users = User.objects.filter(is_admin=False).filter(
            is_school_admin=False
        )
        for u in regular_users:
            u.delete()

        RequestForLessons.objects.all().delete()
        SchoolTerm.objects.all().delete()
        Booking.objects.all().delete()
