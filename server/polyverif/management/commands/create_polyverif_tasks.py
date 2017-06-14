import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from polyverif.models import Project


class Command(BaseCommand):
    help = 'Create polygon verification task.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max_num_tasks',
            action='store',
            dest='max_num_tasks',
            default=5,
            type=int,
            help='Number of tasks to create',
        )

    def handle(self, *args, **options):
        max_num_tasks = options['max_num_tasks']
        project = Project.objects.get(name='PolygonVerification')
        project.create_tasks(max_num_tasks=max_num_tasks)
