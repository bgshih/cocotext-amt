from django.core.management.base import BaseCommand, CommandError

QTYPE_BAN = '3V8AA37DQQKBPY81QYD8HD8VAHIWOS'

class Command(BaseCommand):
    help = 'Ban workers by associating them with banning qualification type (not blocking).'

    def add_arguments(self, parser):
        pass

    def soft_ban_workers(self, workers_id_list):
        

    def handle(self, *args, **options):
        self.create_polyannot_hit_type()
