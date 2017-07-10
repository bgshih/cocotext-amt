from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.models import CocoTextInstance
from polyannot.models import Project, Content


class Command(BaseCommand):
    help = 'Import Polyannot project contents from text instances'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        project = Project.objects.get(name='Polyannot')
        print('Importing Contents from CocoTextInstances...')

        for instance in tqdm(CocoTextInstance.objects.all()):
            if instance.polygon_verification == 'C':
                # instances verified as correct are used as static content
                type = 'ST'
            else:
                # wrong or disputed instances are used as hints
                type = 'HI'

            if not hasattr(instance, 'polyannot_content'):
                # create new content
                Content.objects.create(
                    project       = project,
                    text_instance = instance,
                    type          = type,
                )
            else:
                # update content
                content = instance.polyannot_content
                content.type = type
                content.save()
