import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from polyverif.models import Worker


ADMIN_WORKER = 'AEKCMQGDD2GCJ'


class Command(BaseCommand):
    help = 'Set contents responded by admin as sentinels'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        admin = Worker.objects.get(mturk_worker = ADMIN_WORKER)
        responses = [res for res in admin.responses.all() \
            if res.verification != 'U' and res.content.sentinel == False]
        contents = [res.content for res in responses]

        if len(contents) == 0:
            print('Nothing to set. Aborted.')
            return

        print('Going to set {} contents as sentinels:'.format(len(contents)))
        print(contents)

        if input('Continue? [y/n] ') != 'y':
            print('Aborted')
            return

        for res in tqdm(responses):
            content = res.content
            content.sentinel = True
            content.gt_verification = res.verification
            content.save()
