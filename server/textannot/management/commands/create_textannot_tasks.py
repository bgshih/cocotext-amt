import math
import json
import random
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import MturkHitType, MturkHit
from textannot.models import Project, Task

HIT_QUESTION = """
<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
<ExternalURL>https://polyverif.bgshi.me</ExternalURL>
<FrameHeight>800</FrameHeight>
</ExternalQuestion>
"""

class Command(BaseCommand):
    help = 'Create text annotation task.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max_num_tasks',
            action='store',
            dest='max_num_tasks',
            default=5,
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

    def create_tasks(self,
                     project,
                     num_content_per_task,
                     sentinel_portion,
                     max_num_tasks=None):
        