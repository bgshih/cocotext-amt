import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.models import Experiment


class Command(BaseCommand):
    help = 'Create crowdsourcing experiments.'

    def add_arguments(self, parser):
        pass
    
    def create_polygon_verification_experiment(self, *args, **options):
        experiment_name = 'PolygonVerification'
        try:
            experiment = Experiment.objects.get(name=experiment_name)
        except Experiment.DoesNotExist:
            experiment = Experiment()
            experiment.name = experiment_name
        experiment.max_assignments = 3
        experiment.auto_approval_delay = timedelta(days=2)
        experiment.lifetime = timedelta(days=21)
        experiment.assignment_duration = timedelta(minutes=10)
        experiment.reward = 0.02
        experiment.title = 'Verify these text annotations'
        experiment.keywords = 'image,text,verification'
        experiment.description = 'Check these annotations carefully and mark the images that are not properly annotated.'
        experiment.question = """<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"> <ExternalURL>https://polyverif.bgshi.me</ExternalURL> <FrameHeight>800</FrameHeight> </ExternalQuestion>"""

        experiment.save()

    def handle(self, *args, **options):
        self.create_polygon_verification_experiment(*args, **options)
