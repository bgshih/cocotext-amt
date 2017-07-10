from datetime import timedelta
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import MturkHitType, MturkHit, CocoTextImage
from polyannot.models import Project, Task, Content


HIT_QUESTION = """<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"> <ExternalURL>https://polyannot.bgshi.me</ExternalURL> <FrameHeight>800</FrameHeight> </ExternalQuestion>"""


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
            '--start_image_idx',
            action='store',
            dest='start_image_idx',
            default=0,
            type=int,
            help='Starting index of COCO-Text image',
        )

        parser.add_argument(
            '--max_num_hints_per_image',
            action='store',
            dest='max_num_hints_per_image',
            default=15,
            type=int,
            help='Maximum number of hints displayed on each image'
        )

        parser.add_argument(
            '--hit_type_slug',
            action='store',
            dest='hit_type_slug',
            default='polyannot-main',
            type=str,
            help='Slug name of HIT type'
        )

    def handle(self, *args, **options):
        project = Project.objects.get(name='Polyannot')

        hit_type = MturkHitType.objects.get(slug=options['hit_type_slug'])

        self.create_free_annotation_tasks(
            project         = project,
            hit_type        = hit_type,
            start_image_idx = options['start_image_idx'],
            max_num_tasks   = options['max_num_tasks']
        )

    def create_free_annotation_tasks(self,
                                     project,
                                     hit_type,
                                     start_image_idx,
                                     max_num_tasks):
        """Create free annotation tasks.
        No hints are given. Workers are asked to draw up to n polygons.
        """
        max_num_tasks_possible = CocoTextImage.objects.count() - start_image_idx
        num_tasks = min(max_num_tasks, max_num_tasks_possible)
        image_idx = start_image_idx

        if input('Going to create {} tasks, continue? (y/n)'.format(num_tasks)) != 'y':
            print('Aborted')
            return
        
        for i in range(max_num_tasks):
            image = CocoTextImage.objects.order_by('id')[start_image_idx + i]

            # create HIT
            hit = MturkHit.objects.create(
                hit_type        = hit_type,
                max_assignments = 1,
                lifetime        = timedelta(days=14),
                question        = HIT_QUESTION,
            )

            # create task
            task = Task.objects.create(
                hit=hit,
                project=project,
                image=image
            )

            # assign contents to task
            for instance in image.text_instances.all():
                content = instance.polyannot_content
                content.tasks.add(task)
