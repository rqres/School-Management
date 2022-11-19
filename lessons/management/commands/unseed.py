from django.core.management.base import BaseCommand
from lessons.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        regular_users = User.objects.filter(is_admin=False)
        for u in regular_users:
            u.delete()
