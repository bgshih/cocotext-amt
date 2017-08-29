from django.core.management.base import BaseCommand, CommandError

# from common.models import 
from polyannot.models import ProjectWorker
from common.utils import get_mturk_client


NOTIFICATION_BLACK_LIST = ['A3EI4AOY9AZIQY', 'ADH9I9TEDVL9K', 'A36QWTX7JIIDT9', 'A1VIUV55F27XVM']


class Command(BaseCommand):
    help = 'Notify worker about new HITs'

    def add_arguments(self, parser):
        pass

    def notify_workers(self):
        workers_to_notify = ProjectWorker.objects.exclude(mturk_worker__in=NOTIFICATION_BLACK_LIST)
        # workers = ProjectWorker.objects.filter(id='A1U8NMURJO7EBJ')
        print('Going to notify {} workers:'.format(workers_to_notify.count()))
        worker_ids = [w.mturk_worker.id for w in workers_to_notify]
        print(worker_ids)
        if input('Continue? (y/n) ') == 'y':
            get_mturk_client().notify_workers(
                Subject='200 New HITs Available',
                MessageText="""Hello there! According to our record you performed well in the past HITs. Now we have new HITs available, and we welcome you to come back and work more! Search 'COCO-Text Team' to find these new HITs.""",
                WorkerIds=worker_ids
            )
            print('Notification sent')
        else:
            print('Aborted')

    def handle(self, *args, **options):
      self.notify_workers()
