import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.utils import get_mturk_client
from textannot.models import Project


class Command(BaseCommand):
    help = 'Sync the TextAnnotation project.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        project = Project.objects.get(name='TextAnnotation')
        project.sync()
