from django.core.management.base import BaseCommand, CommandError

# from common.models import 
from polyannot.models import ProjectWorker
from common.utils import get_mturk_client

MINIMUM_ACCURACY = 0.8
# MINIMUM_ACCURACY = 0.7
# NOTIFICATION_BLACK_LIST = ['A3EI4AOY9AZIQY', 'ADH9I9TEDVL9K', 'A36QWTX7JIIDT9', 'A1VIUV55F27XVM']

# SUBJECT_TEXT = """New HITs Available"""
# MESSAGE_TEXT = """Hello there! According to our record you performed well in the past HITs. Now we have new HITs available, and we welcome you to come back and work more! Search 'COCO-Text Team' to find these new HITs.
# """

SUBJECT_TEXT = """Please Avoid This Mistake"""
# MESSAGE_TEXT = """Hello there! Thanks for your hard work! In the PDF at this link https://s3.amazonaws.com/cocotext-amt-resource/CommonMistakes-20170906.pdf I summarized some common mistakes in annotations. Please spend ~1min to read should you take further HITs. Let me know if you have any questions."""

MESSAGE_TEXT = """Hello there! Thanks for your hard work!

We have noticed that some Turkers tend to annotate a string of digits by individual characters. For example: https://s3.amazonaws.com/cocotext-amt-resource/DigitsMistake-20170916.png.

Please be advised that this is NOT correct. Strings of digits such as door numbers, phone numbers should be considered as one word and annotated as one.

Let us know if you have any questions.
"""

# SUBJECT_TEXT = """Common Mistakes Summary (~1min read)"""


class Command(BaseCommand):
    help = 'Notify worker about new HITs'

    def add_arguments(self, parser):
        pass

    def notify_workers(self):
        workers_to_notify = []
        for project_worker in ProjectWorker.objects.all():
            if project_worker.admin_accuracy(return_str=False) > MINIMUM_ACCURACY:
                workers_to_notify.append(project_worker)
        # workers_to_notify = ProjectWorker.objects.exclude(mturk_worker__in=NOTIFICATION_BLACK_LIST)
        # workers = ProjectWorker.objects.filter(id='A1U8NMURJO7EBJ')
        print('Going to notify {} workers:'.format(len(workers_to_notify)))
        worker_ids = [w.mturk_worker.id for w in workers_to_notify]
        print(worker_ids)
        if input('Continue? (y/n) ') == 'y':
            get_mturk_client().notify_workers(
                Subject=SUBJECT_TEXT,
                MessageText=MESSAGE_TEXT,
                WorkerIds=worker_ids
            )
            print('Notification sent')
        else:
            print('Aborted')

    def handle(self, *args, **options):
      self.notify_workers()
