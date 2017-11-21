from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from common.models import MturkHitType, QualificationType


class Command(BaseCommand):
    help = 'Create HITType for polyannot'

    def add_arguments(self, parser):
        pass

    def create_polyannot_hit_type_stage2(self):
        qtype_test = QualificationType.objects.get(slug='annot-verification-test-v3')
        qtype_admin_level = QualificationType.objects.get(slug='polyannot-admin-level-stage2')
        hit_type, created = MturkHitType.objects.get_or_create(
            slug                = 'polyannot-stage2-general',
            auto_approval_delay = timedelta(days=1),
            assignment_duration = timedelta(minutes=45),
            reward              = '0.05',
            title               = 'Draw Polygons On *ALL* Words',
            keywords            = 'Text,Image,COCO-Text,Polygon,Annotation,Label',
            description         = 'Draw polygons around words to surround them tightly',
            qrequirements       = [
                {
                    'QualificationTypeId': qtype_test.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [90,],
                    'RequiredToPreview': False
                },
                {
                    'QualificationTypeId': qtype_admin_level.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [0,],
                    'RequiredToPreview': False
                },
            ]
        )
        print('HitType {} {}'.format(hit_type, 'created' if created else 'exists'))

    def create_polyannot_hit_type_20170828_2(self):
        qtype_test = QualificationType.objects.get(slug='annot-verification-test-v3')
        qtype_admin_level = QualificationType.objects.get(slug='polyannot-admin-level-stage2')

        hit_type, created = MturkHitType.objects.get_or_create(
            slug                = 'polyannot-20170828-2',
            auto_approval_delay = timedelta(days=2),
            assignment_duration = timedelta(minutes=15),
            reward              = '0.08',
            title               = 'Draw Polygons Around Words',
            keywords            = 'Text,Image,COCO-Text,Polygon,Annotation,Label',
            description         = 'Draw polygons around words to surround them tightly',
            qrequirements       = [
                {
                    'QualificationTypeId': qtype_test.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [90,],
                    'RequiredToPreview': False
                },
                {
                    'QualificationTypeId': qtype_admin_level.id,
                    'Comparator': 'GreaterThanOrEqualTo',
                    'IntegerValues': [0,],
                    'RequiredToPreview': False
                },
            ]
        )
        print('HitType {} {}'.format(hit_type, 'created' if created else 'exists'))

    def handle(self, *args, **options):
        # self.create_polyannot_hit_type()
        self.create_polyannot_hit_type_stage2()
