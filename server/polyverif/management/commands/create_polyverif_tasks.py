import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.models import *
from polyverif.models import *


class Command(BaseCommand):
    help = 'Create polygon verification task.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ins_per_task',
            action='store',
            dest='ins_per_task',
            default=9,
            type=int,
            help='Number of instances in a verification task',
        )

        parser.add_argument(
            '--max_num_task',
            action='store',
            dest='max_num_task',
            default=5,
            type=int,
            help='Number of tasks to create',
        )
    
    def create_polyverif_tasks(self, *args, **options):
        max_num_task = options['max_num_task']
        ins_per_task = options['ins_per_task']
        print('Going to create as many as {} polygon verification tasks.'.format(max_num_task))

        experiment = Experiment.objects.get(name='PolygonVerification')

        text_instances_to_verify = CocoTextInstance.objects.filter(polygon_verification='U')

        # total number of instances created for verification
        task_count = 0 # total number of tasks created
        task_ins_count = 0 # number of instances created for the current task

        current_task = None
        for text_instance in text_instances_to_verify:
            if current_task is None:
                current_task = PolygonVerificationTask(experiment=experiment)
                current_task.save(create_hit=True)
                task_count += 1

            try:
                # if already created for verification, then pass
                verif_ins = text_instance.for_polygon_verification
                continue
            except PolygonVerificationInstance.DoesNotExist:
                # create a new instance for verification
                verif_ins = PolygonVerificationInstance(
                    text_instance=text_instance,
                    task=current_task,
                )
                verif_ins.save()
                task_ins_count += 1

                # if full, replace the current task with a new one
                if task_ins_count >= ins_per_task:
                    task_ins_count = 0
                    # tasks reach maximum, stop
                    if task_count >= max_num_task:
                        break
                    current_task = None

    def handle(self, *args, **options):
        self.create_polyverif_tasks(*args, **options)
