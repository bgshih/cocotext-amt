import json
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.models import CocoTextImage, CocoTextInstance


class Command(BaseCommand):
    help = 'Import COCO-Text V1 annotations.'

    def add_arguments(self, parser):
        parser.add_argument('annotation_path')
        parser.add_argument(
            '--max_num_images',
            action='store',
            dest='max_num_images',
            default=None,
            type=int,
            help='Maximum number of images to import',
        )

    def handle(self, *args, **options):
        annot_path = options['annotation_path']
        print('Loading V1 annotations from {}'.format(annot_path))
        with open(annot_path, 'r') as f:
            ct_annot = json.load(f)
        
        image_ids = list(ct_annot['imgs'].keys())
        num_images = len(image_ids)
        if options['max_num_images'] is not None:
            num_images = min(num_images, options['max_num_images'])
        print('Going to import {} images'.format(num_images))

        for i in tqdm(range(num_images)):
            image_id = image_ids[i]
            image_info = ct_annot['imgs'][image_id]

            # ceate and save image object
            try:
                image = CocoTextImage.objects.get(id=image_id)
            except CocoTextImage.DoesNotExist:
                image = CocoTextImage()
                image.id = image_id
            image.width = image_info['width']
            image.height = image_info['height']
            image.filename = image_info['file_name']
            set_to_key = {
                'train': 'TRN',
                'val': 'VAL',
                'test': 'TST'
            }
            image.set = set_to_key[image_info['set']]
            image.save()

            annot_ids = [str(o) for o in ct_annot['imgToAnns'][image_id]]
            for annot_id in annot_ids:
                annot = ct_annot['anns'][annot_id]
                bbox = annot['bbox']
                polygon = [
                    {'x': bbox[0],           'y': bbox[1]},
                    {'x': bbox[0] + bbox[2], 'y': bbox[1]},
                    {'x': bbox[0] + bbox[2], 'y': bbox[1] + bbox[3]},
                    {'x': bbox[0],           'y': bbox[1] + bbox[3]},
                ]

                try:
                    text_instance = CocoTextInstance.objects.get(id=annot_id)
                except CocoTextInstance.DoesNotExist:
                    text_instance = CocoTextInstance()
                    text_instance.id = annot_id

                text_instance.image = image
                text_instance.polygon = polygon

                if 'utf8_string' in annot:
                    text_instance.text = annot['utf8_string']
                else:
                    text_instance.text = None

                legibility_to_key = {
                    'legible': 'L',
                    'illegible': 'I',
                }
                text_instance.legibility = legibility_to_key[annot['legibility']]

                class_to_key = {
                    'machine printed': 'M',
                    'handwritten': 'H',
                    'others': 'O'
                }
                text_instance.text_class = class_to_key[annot['class']]

                text_instance.language = annot['language']

                text_instance.from_v1 = True
                text_instance.polygon_verified = False
                text_instance.text_verified = False
                text_instance.legibility_verified = False
                text_instance.language_verified = False

                text_instance.save()
