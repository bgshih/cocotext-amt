import os
import json
from tqdm import tqdm
import ipdb

from django.core.management.base import BaseCommand, CommandError
from common.models import CocoTextImage


class Command(BaseCommand):
    help = 'Export V2 annotations.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output_directory',
            action='store',
            dest='output_directory',
            default=None,
            type=str,
            help='Directory for output JSONs'
        )
    
    def handle(self, *args, **kwargs):
        output_directory = kwargs['output_directory']
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        
        responses_stat = {}

        for ct_image in tqdm(CocoTextImage.objects.all()):
            json_obj = {
                'image': ct_image.id,
                'width': ct_image.width,
                'height': ct_image.height,
                'text_instances': [],
            }
            for ct_instance in ct_image.text_instances.filter(stage_2=True):
                text_annot_responses = ct_instance.textannot_content.responses.all()
                response_count = text_annot_responses.count()
                if response_count not in responses_stat:
                    responses_stat[response_count] = 0
                responses_stat[response_count] += 1
                
                # get the response by an mturker
                if text_annot_responses.count() > 0:
                    response = text_annot_responses[0]
                    for r in text_annot_responses:
                        if r.project_worker.mturk_worker is not None:
                            response = r
                else:
                    print('Text instance {} has zero response'.format(ct_instance.id))
                    response = None

                text_instance_json = {
                    'polygon': ct_instance.polygon,
                    'text': response.text if response is not None else '',
                    'illegible': response.illegible if response is not None else True,
                    'unknownLanguage': response.unknownLanguage if response is not None else False,
                }
                json_obj['text_instances'].append(text_instance_json)

            output_fname = '{}.json'.format(ct_image.id)
            output_file = os.path.join(output_directory, output_fname)
            with open(output_file, 'w') as f:
                json.dump(json_obj, f)
        
        print('response_stat = {}'.format(responses_stat))