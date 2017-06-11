import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from polyverif.models import PolygonVerificationTask


class Command(BaseCommand):
    help = 'Create crowdsourcing experiments.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        client = get_mturk_client()
        for task in PolygonVerificationTask.objects.all():
            task.sync(client=client)
