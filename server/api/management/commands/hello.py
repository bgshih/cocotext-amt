from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'This is a test help message.'

    def add_argument(self, parser):
        parser.add_argument('test_id', nargs='+', type=int)
    
    def handle(self, *args, **kwargs):
        for test_id in options('test_id'):
            print('test_id = {}'.format(test_id))
