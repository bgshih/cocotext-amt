import math
import json
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import *
from polyverif.models import *


TEST_XML_FILENAME = '/home/ubuntu/cocotext-v2/amt/server/polyverif/qualification/test.xml'
ANSWER_XML_FILENAME = '/home/ubuntu/cocotext-v2/amt/server/polyverif/qualification/answer_key.xml'


class Command(BaseCommand):
    help = 'Initialize Polygon Verification'

    def add_arguments(self, parser):
        pass

    def create_project(self):
        project, created = Project.objects.get_or_create(name='Polyverif')
        print('Project {} {}'.format(project, 'created' if created else 'exists'))

    def create_qtype(self):
        with open(TEST_XML_FILENAME, 'r') as f:
            test_xml = f.read()
        with open(ANSWER_XML_FILENAME, 'r') as f:
            answer_xml = f.read()

        qtype, created = QualificationType.objects.get_or_create(
            name               = '[Test-0.1] Annotation Verification Test',
            keywords           = 'Test,Verification,Text,Image,COCO-Text',
            description        = 'Mark the annotations that are correct by clicking on them.',
            qtype_status       = 'A',
            retry_delay        = timedelta(days=1),
            test               = test_xml,
            test_duration      = timedelta(minutes=30),
            auto_granted       = False,
            answer_key         = answer_xml,
            auto_granted_value = None
        )
        print('QualificationType {} {}'.format(qtype, 'created' if created else 'exists'))
        return qtype.id

    def create_hit_type(self, qtype_id):
        hit_type, created = MturkHitType.objects.get_or_create(
            auto_approval_delay = timedelta(days=2),
            assignment_duration = timedelta(minutes=15),
            reward              = '0.10',
            title               = 'Annotation Verification',
            keywords            = 'Verification,Text,Image,COCO-Text',
            description         = 'Mark the annotations that are correct by clicking on them.',
            qrequirements       = [
                {
                    'QualificationTypeId': qtype_id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [90,],
                    'RequiredToPreview': False
                }
            ]
        )
        print('HitType {} {}'.format(hit_type, 'created' if created else 'exists'))

    def handle(self, *args, **options):
        self.create_project()
        qtype_id = self.create_qtype()
        self.create_hit_type(qtype_id)
