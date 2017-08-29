from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Create a qualification type'

    def add_arguments(self, parser):
        pass
    