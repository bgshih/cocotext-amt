import math
import json
import random
import logging
from tqdm import tqdm
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import MturkHitType, MturkHit, QualificationType
from textannot.models import Project, Task, Content

# logging.warning('USING LOCALHOST IN HIT QUESTION, REPLACE IT WITH REMOTE SERVER IN DEPLOYMENT')

HIT_QUESTION = """
<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
<ExternalURL>https://textannot.bgshi.me</ExternalURL>
<FrameHeight>1700</FrameHeight>
</ExternalQuestion>
"""

class Command(BaseCommand):
    help = 'Create text annotation task.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_tasks',
            action='store',
            dest='num_tasks',
            default=2,
            type=int,
            help='Number of tasks to create',
        )
        parser.add_argument(
            '--num_content_per_task',
            action='store',
            dest='num_content_per_task',
            default=12,
            type=int,
            help='Number of contents per task'
        )
        parser.add_argument(
            '--sentinel_portion',
            action='store',
            dest='sentinel_portion',
            default=0.1,
            type=float,
            help='Portion of sentinel contents'
        )
        parser.add_argument(
            '--include_dispute',
            action='store',
            dest='include_dispute',
            default=False,
            type=bool,
            help='Include disputed contents')

    def handle(self, *args, **options):
        # self.create_hit_type()
        project = Project.objects.get(name='TextAnnotation')
        self.create_tasks(
            project=project,
            num_content_per_task=options['num_content_per_task'],
            sentinel_portion=options['sentinel_portion'],
            include_dispute=options['include_dispute'],
            num_tasks=options['num_tasks'])

    def create_hit_type(self):
        qtype_test = QualificationType.objects.get(slug='textannot-test-v1')
        hit_type, created = MturkHitType.objects.get_or_create(
            slug='textannot-v2',
            auto_approval_delay=timedelta(days=1),
            assignment_duration=timedelta(minutes=30),
            reward='0.04',
            title='Annotate text in every image',
            keywords='Transcription,Text,Annotation,Label',
            description='Annotate text in every image',
            qrequirements=[
                {
                    'QualificationTypeId': qtype_test.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [80,],
                    'RequiredToPreview': False
                }
            ]
        )
        print('HitType {} {}'.format(hit_type, 'created' if created else 'exists'))

    def create_tasks(self,
                     project=None,
                     num_content_per_task=None,
                     sentinel_portion=None,
                     include_dispute=False,
                     num_tasks=None):
        contents = Content.objects.filter(status='U')
        if include_dispute:
            contents.union(Content.objects.filter(status='D'))
        num_contents = contents.count()
        print('Remaining contents: {}'.format(num_contents))

        # contents change during task creation
        contents = list(contents.all())

        num_tasks_to_create = min(num_contents // num_content_per_task, num_tasks)
        if input('Going to create {} tasks, continue? (y/n) '.format(num_tasks_to_create)) != 'y':
            print('Aborted')
            return

        project = Project.objects.get(name='TextAnnotation')
        hit_type = MturkHitType.objects.get(slug='textannot-v2')

        for i in range(num_tasks_to_create):
            hit = MturkHit.objects.create(
                hit_type        = hit_type,
                max_assignments = 1,
                lifetime        = timedelta(days=7),
                question        = HIT_QUESTION,
            )
            task = Task.objects.create(hit=hit, project=project)

            content_count = 0
            for j in range(num_content_per_task):
                content_index = i * num_content_per_task + j
                if content_index >= num_contents:
                    break
                else:
                    content = contents[content_index]
                    content.tasks.add(task)
                    content.save()
                    content_count += 1
            print('[{}/{}] Created HIT {} with {} contents'.format(i+1, num_tasks_to_create, hit.id, content_count))
