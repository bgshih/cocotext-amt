import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from polyverif.models import Project


class Command(BaseCommand):
    help = 'Sync PolygonVerification project.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        client = get_mturk_client()
        project = Project.objects.get(name='PolygonVerification')
        project.sync(client=client)
