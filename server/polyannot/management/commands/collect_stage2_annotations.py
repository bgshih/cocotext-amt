from django.db.models import Count, Case, When, IntegerField
from django.core.management.base import BaseCommand, CommandError

from common.models import MturkHitType, MturkHit, CocoTextImage
from polyannot.models import Project, Task, Submission


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        project = Project.objects.get(name='Polyannot')
        self.collect_stage2_annotations(project=project)

    def collect_stage2_annotations(self, project):
        stage2_hits = MturkHit.objects.filter(hit_type='39I6UD9LVJWMG2FU1GOQCZH5SFAN6D')
        for hit in stage2_hits:
            task = hit.polyannot_task
            submissions = task.submissions
            if submissions.count() == 0:
                print('No submissions found for task {}'.format(task))
                continue
            submission = submissions.all()[0]
            
            # get all annotations
            annotations = []
            for response in submission.responses.all():
                polygon = response.text_instance.polygon
                annotations.append({'polygon': polygon})
            polygons = [annt['polygon'] for annt in annotations]
            
            image = task.image
            image.misc_info['stage2'] = {
              'polygons': polygons
            }

            image.save()
