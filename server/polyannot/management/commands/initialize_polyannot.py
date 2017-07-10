import math
import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import *
from polyannot.models import *


class Command(BaseCommand):
    help = 'Create QualificationType and HITType for PolygonVerification'

    def add_arguments(self, parser):
        pass

    def create_project(self):
        project, created = Project.objects.get_or_create(name='Polyannot')
        print('Project {} {}'.format(project, 'created' if created else 'exists'))

    def create_hit_type(self, qtype):
        hit_type, created = MturkHitType.objects.get_or_create(
            slug                = 'polyannot-main',
            auto_approval_delay = timedelta(days=2),
            assignment_duration = timedelta(minutes=15),
            reward              = '0.05',
            title               = 'Draw Polygons Around Words',
            keywords            = 'Text,Image,COCO-Text,Polygon,Annotation,Label',
            description         = 'Draw polygons around words to surround them tightly',
            qrequirements       = [
                {
                    'QualificationTypeId': qtype.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [90,],
                    'RequiredToPreview': False
                }
            ]
        )
        print('HitType {} {}'.format(hit_type, 'created' if created else 'exists'))

    def handle(self, *args, **options):
        self.create_project()

        # both polyannot and polyverif use the "annot-verification-test" qualification type
        qtype = QualificationType.objects.get(slug='annot-verification-test')

        self.create_hit_type(qtype)
