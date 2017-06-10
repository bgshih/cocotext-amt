import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from api.utils import get_mturk_client
from api.models import MturkHit


class Command(BaseCommand):
    help = 'Clean AMT HITs that are not associated with database objects.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        client = get_mturk_client()
        next_token = None
        response = client.list_hits(MaxResults=100)
        hits = response['HITs']
        for hit in hits:
            print(hit['HITId'], hit['HITStatus'], hit['HITReviewStatus'])

        for hit in hits:
            if hit['HITStatus'] != 'Assignable':
                pass

        raise NotImplementedError('TODO: I have not find a way to delete assignable HITs.')
