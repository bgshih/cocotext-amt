import math
import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from api.models import Experiment, MturkHit, CocoTextInstance, PolygonVerificationTask, \
    TextInstanceForPolygonVerification


class Command(BaseCommand):
    help = 'Create crowdsourcing experiments.'

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
            default=3,
            type=int,
            help='Number of tasks to create',
        )

        parser.add_argument(
            '--permute',
            action='store_true',
            dest='permute',
            default=False,
            help='Whether to permute instances',
        )
    
    def create_polyverif_tasks(self, *args, **options):
        max_num_task = options['max_num_task']
        ins_per_task = options['ins_per_task']

        experiment = Experiment.objects.get(name='PolygonVerification')
        text_instances_to_verify = CocoTextInstance.objects.filter(polygon_verification='U')
        print('Going to create as many as {} polygon verification tasks.'.format(max_num_task))

        # total number of instances created for verification
        task_count = 0 # total number of tasks created
        task_ins_count = 0 # number of instances created for the current task

        current_task = None
        for text_instance in text_instances_to_verify:
            if current_task is None:
                current_task = PolygonVerificationTask()
                current_task.experiment = experiment
                current_task.save(create_hit=True)
                task_count += 1

            try:
                # if already created for verification, then pass
                TextInstanceForPolygonVerification.objects.get(id=text_instance.id)
                continue
            except TextInstanceForPolygonVerification.DoesNotExist:
                # create a new instance for verification
                ins_verif = TextInstanceForPolygonVerification()
                ins_verif.id = text_instance.id
                ins_verif.text_instance = text_instance
                ins_verif.verification_task = current_task
                ins_verif.verification_status = 'UV'
                ins_verif.save()
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
