import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from common.models import MturkHit


class Command(BaseCommand):
    help = 'Sync HIT status with MTurk'

    def add_arguments(self, parser):
        pass
    
    def sync_all_hits(self):
        print('Syncing all HITs')
        for hit in tqdm(MturkHit.objects.all()):
            hit.sync(sync_assignments=True)

    def handle(self, *args, **options):
        self.sync_all_hits()
