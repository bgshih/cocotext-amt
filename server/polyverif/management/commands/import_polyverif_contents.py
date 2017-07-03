import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.models import CocoTextInstance
from polyverif.models import Project, Content


class Command(BaseCommand):
    help = 'Import PolygonVerification project contents from text instances'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        project = Project.objects.get(name='Polyverif')
        print('Retrieving CocoTextInstances...')
        instances_to_verify = CocoTextInstance.objects.filter(polygon_verification='U')

        for text_instance in tqdm(instances_to_verify):
            Content.objects.get_or_create(
                status='U',
                project=project,
                text_instance=text_instance
            )
