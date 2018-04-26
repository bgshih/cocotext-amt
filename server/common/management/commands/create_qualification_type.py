from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.models import QualificationType


class Command(BaseCommand):
    help = 'Create a qualification type'

    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **kwargs):
        self.create_textannot_qtype()

    def create_textannot_qtype(self):
        with open('textannot/qualification/test.xml') as f:
            test_str = f.read()
        qtype = QualificationType(
            id=None,
            name='Text Annotation Test',
            keywords='Transcription, Text',
            description='Annotate text in every image',
            test=test_str,
            test_duration=timedelta(minutes=15),
            answer_key=None,
            retry_delay=timedelta(minutes=30),
            auto_granted=False,
            slug='textannot-test-v1',
        )
        qtype.save()
