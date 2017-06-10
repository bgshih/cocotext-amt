import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from api.models import *

ADMIN_WORKER_ID = 'AEKCMQGDD2GCJ' # bgshiaws@gmail.com


class Command(BaseCommand):
    help = 'Pick up instances and set them as sentinels.'

    def add_arguments(self, parser):
        pass

    def pick_sentinels(self, *args, **options):
        """ Answers by admin are picked as sentinels """

        sentinel_answers = {}
        for verif_ins in TextInstanceForPolygonVerification.objects.all():
            # if admin has veriied this instance, mark it as sentinel
            instance_answers = verif_ins.retrieve_answers()
            if ADMIN_WORKER_ID in instance_answers and instance_answers[ADMIN_WORKER_ID] != 'U':
                sentinel_answers[verif_ins.id] = instance_answers[ADMIN_WORKER_ID]

        # prompt
        sentinel_ids = list(sentinel_answers.keys())
        print('Going to make these instances sentinels: {}'.format(sentinel_ids))
        if input('Continue? (y/n)') != 'y':
            print('Canceled')
            return

        for sentinel_id in sentinel_ids:
            text_instance = CocoTextInstance.objects.get(id=sentinel_id)
            text_instance.polygon_verification = sentinel_answers[sentinel_id]
            text_instance.save()


    def handle(self, *args, **options):
        self.pick_sentinels(self, *args, **options)
