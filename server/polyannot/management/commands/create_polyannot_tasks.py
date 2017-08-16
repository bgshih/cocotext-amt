from datetime import timedelta
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Count, Case, When, IntegerField

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
            help='Maximum number of tasks to create',
        )

        parser.add_argument(
            '--num_v1_instances_range',
            action='store',
            dest='num_v1_instances_range',
            nargs=2,
            default=[0, 0],
            help='Range of number of V1 instances.'
        )

        parser.add_argument(
            '--start_idx_within_qset',
            action='store',
            dest='start_idx_within_qset',
            type=int,
            default=0,
            help='Starting index within the filtered query set'
        )

        parser.add_argument(
            '--hit_type_slug',
            action='store',
            dest='hit_type_slug',
            default='polyannot-main',
            type=str,
            help='Slug name of the HIT type to use'
        )

    def handle(self, *args, **options):
        project = Project.objects.get(name='Polyannot')
        hit_type = MturkHitType.objects.get(slug=options['hit_type_slug'])

        self.create_free_annotation_tasks(
            project         = project,
            hit_type        = hit_type,
            start_idx_within_qset = options['start_idx_within_qset'],
            max_num_tasks   = options['max_num_tasks'],
            num_v1_instances_range = tuple([int(o) for o in options['num_v1_instances_range']]),
        )

    def create_free_annotation_tasks(self,
                                     project,
                                     hit_type,
                                     start_idx_within_qset,
                                     max_num_tasks,
                                     num_v1_instances_range):
        """Create free annotation tasks.
        No hints are given. Workers are asked to draw up to n polygons.
        """

        min_num_v1_instances, max_num_v1_instances = num_v1_instances_range

        # filter images by the number of v1 instances
        qset = CocoTextImage.objects.annotate(
            num_v1_instances=Count(
                Case(
                    When(text_instances__from_v1__exact=True, then=1),
                    output_field=IntegerField()
                )
            )
        )
        qset = qset.filter(
            num_v1_instances__gte=min_num_v1_instances,
            num_v1_instances__lte=max_num_v1_instances
        )
        images_set = qset[start_idx_within_qset:start_idx_within_qset+max_num_tasks]

        if input('Going to create {} tasks, continue? (y/n)'.format(images_set.count())) != 'y':
            print('Aborted')
            return
        
        for i, image in enumerate(images_set):
            hit = MturkHit.objects.create(
                hit_type        = hit_type,
                max_assignments = 1,
                lifetime        = timedelta(days=7),
                question        = HIT_QUESTION,
            )
            task = Task.objects.create(
                hit=hit,
                project=project,
                image=image
            )
