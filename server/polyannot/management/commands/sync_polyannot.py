import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from polyannot.models import Project


class Command(BaseCommand):
    help = 'Sync Polyannot project.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project_name',
            action='store',
            dest='project_name',
            default='Polyannot',
            type=str,
            help='Project to sync',
        )

        parser.add_argument(
            '--skip_completed',
            action='store',
            dest='skip_completed',
            default=True,
            type=bool,
            help='Whether to skip completed tasks',
        )

    def handle(self, *args, **options):
        project = Project.objects.get(name=options['project_name'])
        project.sync(skip_completed_tasks=options['skip_completed'])
