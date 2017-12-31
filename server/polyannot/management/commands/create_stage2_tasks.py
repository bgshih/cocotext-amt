from datetime import timedelta
import logging

from django.db.models import Count, Case, When, IntegerField
from django.core.management.base import BaseCommand, CommandError

from common.models import MturkHitType, MturkHit, CocoTextImage
from polyannot.models import Project, Task

HIT_QUESTION = """<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"> <ExternalURL>https://polyannot.bgshi.me</ExternalURL> <FrameHeight>800</FrameHeight> </ExternalQuestion>"""


class Command(BaseCommand):
    help = 'Create polygon annotation stage2 tasks.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max_num_tasks',
            action='store',
            dest='max_num_tasks',
            default=5,
            type=int,
            help='Maximum number of tasks to create')

        parser.add_argument(
            '--start_idx_within_qset',
            action='store',
            dest='start_idx_within_qset',
            type=int,
            default=0,
            help='Starting index within the filtered query set')

        parser.add_argument(
            '--hit_type_slug',
            action='store',
            dest='hit_type_slug',
            default='polyannot-stage2',
            help='Slug name of the HIT type to use')

        parser.add_argument(
            '--repost',
            action='store',
            dest='repost',
            default=False,
            help='Repost unfinished HITs')

    def handle(self, *args, **kwargs):
        project = Project.objects.get(name='Polyannot')
        hit_type = MturkHitType.objects.get(slug=kwargs['hit_type_slug'])

        if not kwargs['repost']:
            self.create_stage2_annotation_tasks(
                project=project,
                hit_type=hit_type,
                start_idx_within_qset=kwargs['start_idx_within_qset'],
                max_num_tasks=kwargs['max_num_tasks'])
        else:
            self.repost_unfinished_hits(
                project=project,
                hit_type=hit_type,
                start_idx_within_qset=kwargs['start_idx_within_qset'],
                max_num_tasks=kwargs['max_num_tasks'])

    def _get_stage2_image_list(self):
        """Get the list of images that are verified as
        incorrect or incomplete by admin or turker.
        """
        image_list = []
        print('Getting the list of unannotated images...')
        for image in CocoTextImage.objects.all():
            if image.misc_info is not None and image.misc_info['stage1']['completed'] == False and len(image.misc_info['stage1']['polygons']) > 0:
                image_list.append(image)
        print('Retrieved {} images'.format(len(image_list)))
        return image_list

    def create_stage2_annotation_tasks(self,
                                       project=None,
                                       hit_type=None,
                                       start_idx_within_qset=0,
                                       max_num_tasks=0):
        image_list = self._get_stage2_image_list()
        image_list = image_list[start_idx_within_qset:start_idx_within_qset+max_num_tasks]

        if input('Going to create {} tasks, continue? (y/n) '.format(len(image_list))) != 'y':
            print('Aborted')
            return

        for image in image_list:
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

    def repost_unfinished_hits(self,
                               project=None,
                               hit_type=None,
                               start_idx_within_qset=0,
                               max_num_tasks=0):
        stage2_hits = MturkHit.objects.filter(hit_type='39I6UD9LVJWMG2FU1GOQCZH5SFAN6D')

        image_list = []

        for hit in stage2_hits:
            task = hit.polyannot_task
            if task.submissions.count() == 0:
                # not submitted, need repost
                image_list.append(task.image)

        print('Retrieved {} unfinished images'.format(len(image_list)))

        image_list = image_list[start_idx_within_qset:start_idx_within_qset+max_num_tasks]

        if input('Going to repost {} tasks, continue? (y/n) '.format(len(image_list))) != 'y':
            print('Aborted')
            return

        for image in image_list:
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