import os
import json
from tqdm import tqdm
import ipdb

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from common.models import CocoTextImage


SET_LABEL_MAP = {
    'TRN': 0,
    'VAL': 1,
    'TST': 2,
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
            action='store',
            dest='include_test',
            default=False,
            type=bool,
            help='Export test annotations as well',
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

        image_list_filename = os.path.join(export_directory, 'image_list.json')

        if kwargs['include_test']:
            ct_image_queryset = CocoTextImage.objects.all()
        else:
            ct_image_queryset = CocoTextImage.objects.filter(~Q(set = 'TST'))
        ct_image_list = list(ct_image_queryset)

        print('Creating image_list.json')
        image_list_json = {'image_list': []}
        for ct_image in tqdm(ct_image_list):
            image_json_obj = {
                'image_id': ct_image.id,
                'width': ct_image.width,
                'height': ct_image.height,
                'filename': ct_image.filename,
                'set': SET_LABEL_MAP[ct_image.set],
            }
            image_list_json['image_list'].append(image_json_obj)
        with open(image_list_filename, 'w') as f:
            json.dump(image_list_json, f)

        print('Creating annotations jsons')
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
                text_instance_json = {
                    'instance_id': ct_instance.id,
                    'mask': mask,
                    'text': response.text if response is not None else '',
                    'legibility': legibility_label,
                    'type': class_label,
                    'language': language_label,
                }
                annotation_json['annotations'].append(text_instance_json)

            output_fname = '{}.json'.format(ct_image.id)
            output_file = os.path.join(export_directory, output_fname)
            with open(output_file, 'w') as f:
                json.dump(annotation_json, f)
        
        # print('response_stat = {}'.format(responses_stat))

    def export_to_single_file(self, *args, **kwargs):
        raise NotImplementedError
