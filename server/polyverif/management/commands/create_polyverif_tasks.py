import math
import json
import random
from tqdm import tqdm
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import MturkHitType, MturkHit
from polyverif.models import Project, Task


HIT_QUESTION = """<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"> <ExternalURL>https://polyverif.bgshi.me</ExternalURL> <FrameHeight>800</FrameHeight> </ExternalQuestion>"""


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

        parser.add_argument(
            '--num_content_per_task',
            action='store',
            dest='num_content_per_task',
            default=15,
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
        """Create new tasks from pending and sentinel contents """
        # constants
        # num_content_per_task = settings.POLYVERIF_NUM_CONTENT_PER_TASK
        # sentinel_portion = settings.POLYVERIF_SENTINEL_PORTION

        unassigned_contents = project.contents.filter(status='U')
        sentinel_contents = project.contents.filter(sentinel=True)
        num_sentinel = sentinel_contents.count()

        if num_sentinel == 0:
            sentinel_portion = 0

        max_num_tasks_possible = int((unassigned_contents.count() / (1 - sentinel_portion)) / num_content_per_task)

        if max_num_tasks is None:
            # assign all unassigned
            num_tasks = max_num_tasks_possible
            num_to_assign = unassigned_contents.count()
        else:
            num_tasks = min(max_num_tasks_possible, max_num_tasks)
            num_to_assign = int(num_tasks * num_content_per_task * (1 - sentinel_portion))

        num_total_contents = num_tasks * num_content_per_task
        num_sentinel_to_assign = num_total_contents - num_to_assign

        # prompt for continue
        print('Going to create %d tasks for %d unassigned contents and %d sentinel contents' % \
              (num_tasks, num_to_assign, num_sentinel_to_assign))
        if input('Continue? [y/n] ') != 'y':
            print('Aborted.')
            return

        # positive number means the index of content to assign
        # negative number means the (-index-1) of sentinel
        content_indices = [-(i % num_sentinel + 1) for i in range(num_sentinel_to_assign)] + \
                          list(range(num_to_assign))
        random.shuffle(content_indices)

        # hit_type = MturkHitType.objects.get(id='3FKWIKNZF8P1QWGMRRQEZFI531R7E5')
        hit_type = MturkHitType.objects.get(slug='polyverif-main')

        for i in range(num_tasks):
            # create HIT
            hit = MturkHit.objects.create(
                hit_type        = hit_type,
                max_assignments = 2,
                lifetime        = timedelta(minutes=15),
                question        = HIT_QUESTION,
            )

            # create task
            task, created = Task.objects.get_or_create(
                hit     = hit,
                project = project
            )
            print('Task {} {}'.format(task, 'created' if created else 'exists'))

            # assign contents for this task
            for j in range(num_content_per_task):
                content_index = content_indices[i * num_content_per_task + j]
                if content_index < 0:
                    content = sentinel_contents[-content_index - 1]
                else:
                    content = unassigned_contents[content_index]
                content.tasks.add(task)
                content.save()


    def handle(self, *args, **options):
        project = Project.objects.get(name='Polyverif')
        self.create_tasks(
            project              = project,
            num_content_per_task = options['num_content_per_task'],
            sentinel_portion     = options['sentinel_portion'],
            max_num_tasks        = options['max_num_tasks']
        )
