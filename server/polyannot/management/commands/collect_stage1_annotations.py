from django.db.models import Count, Case, When, IntegerField
from django.core.management.base import BaseCommand, CommandError

from common.models import MturkHitType, MturkHit, CocoTextImage
from polyannot.models import Project, Task, Submission


class Command(BaseCommand):
    help = 'Collect stage1 annotations and store them in a special field in CocoTextImage object'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        project = Project.objects.get(name='Polyannot')
        self.collect_stage1_annotations(project=project)

    def collect_stage1_annotations(self, project=None):
        complete_count = 0
        incomplete_count = 0

        for i, image in enumerate(CocoTextImage.objects.all()):
            if image.text_instances.filter(from_v1=True).count() == 0:
                continue

            assert image.tasks.count() == 1, 'Image {} has no task created'.format(image)
            task = image.tasks.all()[0]
            assert task.submissions.count() == 1, 'Task {} has no submission'.format(task)

            if image.misc_info is None:
                image.misc_info = {'stage1': {}}

            submission = task.submissions.all()[0]

            keep_annotations = False
            completed = False
            admin_mark = submission.admin_mark
            user_mark = None
            if submission.misc_info is not None and \
               'user_marks' in submission.misc_info:
               user_mark = submission.misc_info['user_marks']['A383I2LLYX9LJM']

            mark = None
            if admin_mark != 'U':
                mark = admin_mark
            elif user_mark is not None and user_mark != 'U':
                mark = user_mark

            if mark == 'C':
                image.misc_info['stage1']['polygons'] = submission.answer['polygons']
                image.misc_info['stage1']['completed'] = True
                complete_count += 1
            elif mark == 'R':
                image.misc_info['stage1']['polygons'] = submission.answer['polygons']
                image.misc_info['stage1']['completed'] = False
                incomplete_count += 1
            else:
                image.misc_info['stage1']['polygons'] = {}
                image.misc_info['stage1']['completed'] = False
                incomplete_count += 1

            image.save()
            
            if i % 1000 == 0:
                print('Visited {} images'.format(i))

        print('{} completed, {} incomplete'.format(complete_count, incomplete_count))
