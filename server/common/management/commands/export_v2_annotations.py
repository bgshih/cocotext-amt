import os
import json
from tqdm import tqdm
import ipdb

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from common.models import CocoTextImage
from corrections.models import InstanceCorrection

from shapely.geometry import Polygon

# INSTANCE ID NUMBERING RULE
# Sort images by their integer ID values
# Sort instances by their creation time
# Train and validation instances: count from 1
# Test instances: count from 10,000,000


SET_LABEL_MAP = {
    'TRN': 0,
    'VAL': 1,
    'TST': 2,
}

SET_STRING_MAP = {
    'TRN': 'train',
    'VAL': 'val',
    'TST': 'test'
}

LANG_STRING_MAP = {
    0: 'english',
    1: 'not english',
}

LEGIBILITY_STRING_MAP = {
    0: 'legible',
    1: 'illegible',
}

CLASS_STRING_MAP = {
    0: 'machine printed',
    1: 'handwritten'
}

class Command(BaseCommand):
    help = 'Export V2 annotations.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export_type',
            action='store',
            dest='export_type',
            default='directory',
            type=str,
            help='Export a single file or a directory'
        )
        parser.add_argument(
            '--include_test',
            action='store_true',
            dest='include_test',
            default=False,
            help='Export test annotations as well',
        )
        parser.add_argument(
            '--dont_apply_correction',
            action='store_false',
            dest='apply_correction',
            default=True,
            help='Do not apply corrections',
        )
        parser.add_argument(
            '--export_directory',
            action='store',
            dest='export_directory',
            default=None,
            type=str,
            help='Directory for output JSONs'
        )
    
    def handle(self, *args, **kwargs):
        export_type = kwargs['export_type']
        if export_type == 'directory':
            self.export_to_directory(*args, **kwargs)
        elif export_type == 'single_file':
            self.export_to_single_file(*args, **kwargs)
        else:
            raise ValueError('Unkonwn export type: {}'.format(export_type))

    def export_to_directory(self, *args, **kwargs):
        export_directory = kwargs['export_directory']
        if not os.path.exists(export_directory):
            os.mkdir(export_directory)
        # responses_stat = {}

        image_list_filename = os.path.join(export_directory, '../image_list.json')

        if kwargs['include_test'] == True:
            ct_image_queryset = CocoTextImage.objects.all()
        else:
            ct_image_queryset = CocoTextImage.objects.filter(~Q(set='TST')).all() # not test
            print('{}'.format(ct_image_queryset.count()))
        ct_image_queryset = ct_image_queryset.order_by('id')
        ct_image_list = list(ct_image_queryset)

        print('Creating image_list.min.json')
        image_list_json = {'image_list_min': []}
        for ct_image in ct_image_list:
            image_list_json['image_list_min'].append(int(ct_image.id))
        with open(image_list_filename, 'w') as f:
            json.dump(image_list_json, f)

        TRAINVAL_INSTANCE_ID_COUNT = 1
        TEST_INSTANCE_ID_COUNT = 10000000

        print('Creating annotations jsons')
        corrections_count = 0
        for ct_image in tqdm(ct_image_list):
            annotation_json = {'annotations': []}
            for ct_instance in ct_image.text_instances.filter(stage_2=True):
                text_annot_responses = ct_instance.textannot_content.responses.all()
                # response_count = text_annot_responses.count()
                # if response_count not in responses_stat:
                #     responses_stat[response_count] = 0
                # responses_stat[response_count] += 1
                
                # get the response by an mturker
                if text_annot_responses.count() > 0:
                    response = text_annot_responses[0]
                    for r in text_annot_responses:
                        if r.project_worker.mturk_worker is not None:
                            response = r
                else:
                    print('Text instance {} has zero response'.format(ct_instance.id))
                    response = None

                mask = []
                for point in ct_instance.polygon:
                    mask.append(point['x'])
                    mask.append(point['y'])
                illegible = response.illegible if response is not None else False
                legibility_label = 0 if illegible == False else 1
                unknownLanguage = response.unknownLanguage if response is not None else False
                language_label = 0 if unknownLanguage == False else 1
                class_label = 0 # not labeled yet, default to machine printed

                if ct_image.set == 'TST':
                    instance_id = TEST_INSTANCE_ID_COUNT
                    TEST_INSTANCE_ID_COUNT += 1
                else:
                    instance_id = TRAINVAL_INSTANCE_ID_COUNT
                    TRAINVAL_INSTANCE_ID_COUNT += 1

                text_instance_json = {
                    'instance_id': instance_id,
                    'mask': [round(p, 1) for p in mask],
                    'text': response.text if response is not None else '',
                    'legibility': legibility_label,
                    'type': class_label,
                    'language': language_label,
                }

                if kwargs['apply_correction'] == True:
                    corrections_qset = InstanceCorrection.objects.filter(ct_instance=ct_instance)
                    if corrections_qset.exists():
                        corrections = corrections_qset.all()[0].correction
                        assert corrections['instance_id'] == ct_instance.id
                        text_instance_json = {
                            'instance_id': instance_id,
                            'mask': [round(p, 1) for p in corrections['mask']],
                            'text': corrections['text'],
                            'legibility': corrections['legibility'],
                            'type': corrections['type'],
                            'language': corrections['language'],
                        }
                        corrections_count += 1

                annotation_json['annotations'].append(text_instance_json)

            output_fname = '{}.json'.format(ct_image.id)
            output_file = os.path.join(export_directory, output_fname)
            with open(output_file, 'w') as f:
                json.dump(annotation_json, f)
        
        # print('response_stat = {}'.format(responses_stat))
        print('Corrections made: {}'.format(corrections_count))
        print('TRAINVAL_INSTANCE_ID_COUNT = {}'.format(TRAINVAL_INSTANCE_ID_COUNT))
        print('TEST_INSTANCE_ID_COUNT = {}'.format(TEST_INSTANCE_ID_COUNT))

    def export_to_single_file(self, *args, **kwargs):
        if kwargs['include_test'] == True:
            ct_image_queryset = CocoTextImage.objects.all()
        else:
            ct_image_queryset = CocoTextImage.objects.filter(~Q(set='TST')).all() # not test
            print('{}'.format(ct_image_queryset.count()))
        ct_image_queryset = ct_image_queryset.order_by('id')
        ct_image_list = list(ct_image_queryset)

        TRAINVAL_INSTANCE_ID_COUNT = 1
        TEST_INSTANCE_ID_COUNT = 10000000

        coco_json = {
            "imgs": {},
            "cats": {},
            "imgToAnns": {},
            "anns": {},
            "info": {}
        }

        print('Filling imgs, imgToAnns, and anns...')
        for ct_image in ct_image_list:
            image_id = int(ct_image.id)
            image_json = {
                "id": image_id,
                "file_name": ct_image.filename,
                "set": SET_STRING_MAP[ct_image.set],
                "width": ct_image.width,
                "height": ct_image.height,
            }
            coco_json["imgs"][str(image_id)] = image_json

            coco_json['imgToAnns'][str(image_id)] = []

            # load annotations from the files created by export_to_directory
            annotation_filename = os.path.join(
                kwargs['export_directory'],
                '{}.json'.format(image_id))
            with open(annotation_filename, 'r') as f:
                annotation_json = json.load(f)
            
            for text_instance_json in annotation_json['annotations']:
                instance_id = text_instance_json['instance_id']
                coco_json['imgToAnns'][str(image_id)].append(instance_id)

                coordinate_iter = iter(text_instance_json['mask'])
                mask_polygon = Polygon(zip(coordinate_iter, coordinate_iter))
                bbox_xmin, bbox_ymin, bbox_xmax, bbox_ymax = mask_polygon.bounds
                bbox = [bbox_xmin, bbox_ymin, bbox_xmax-bbox_xmin, bbox_ymax-bbox_ymin]

                coco_json['anns'][str(instance_id)] = {
                    'id': instance_id,
                    'mask': text_instance_json['mask'],
                    'bbox': [round(x, 1) for x in bbox],
                    'language': LANG_STRING_MAP[text_instance_json['language']],
                    'area': round(mask_polygon.area, 2),
                    'utf8_string': text_instance_json['text'],
                    'image_id': image_id,
                    'legibility': LEGIBILITY_STRING_MAP[text_instance_json['legibility']],
                    'class': CLASS_STRING_MAP[text_instance_json['type']],
                }

        coco_json_filename = os.path.join(kwargs['export_directory'], '../cocotext.v3.json')
        with open(coco_json_filename, 'w') as f:
            json.dump(coco_json, f, separators=(',', ':'))
        print('Annotations written to {}'.format(coco_json_filename))