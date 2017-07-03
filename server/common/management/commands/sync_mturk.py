import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from common.models import MturkHit, QualificationType, QualificationRequest


class Command(BaseCommand):
    help = 'Sync HIT status with MTurk'

    def add_arguments(self, parser):
        pass
    
    def sync_hits(self):
        print('Syncing all HITs')
        for hit in tqdm(MturkHit.objects.all()):
            hit.sync(sync_assignments=True)

    def sync_qrequests(self):
        print('Synching qualification requests')
        for qtype in QualificationType.objects.all():
            qtype.sync(sync_requests=True)

    def handle(self, *args, **options):
        self.sync_hits()
        self.sync_qrequests()
