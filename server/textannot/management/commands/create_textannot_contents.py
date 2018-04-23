import re
import logging
from os.path import join, exists, splitext
from tqdm import tqdm

import numpy as np
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from common.models import CocoTextImage, CocoTextInstance
from textannot.models import Project, Content, ProjectWorker, Response


class Command(BaseCommand):
  help = 'Create TextAnnot contents and text instances'

  def add_arguments(self, parser):
    parser.add_argument(
      '--crop_directory',
      action='store',
      dest='crop_directory',
      default='',
      type=str,
      help='Directory for saving crops',
    )
    parser.add_argument(
      '--pre_annotation_path',
      action='store',
      dest='pre_annotation_path',
      default='',
      type=str,
      help='File storing pre-annotation results',
    )

  def handle(self, *args, **options):
    # self.create_text_instances(options)
    # self.create_contents()
    self.import_aster_recognition_results(options['pre_annotation_path'])

  def create_text_instances(self, options):
    crop_directory = options['crop_directory']

    for ct_image in tqdm(CocoTextImage.objects.all()):
      if ct_image.misc_info is not None:
        # load COCO image
        coco_image_filename = ct_image.filename
        crop_sub_directory = join(crop_directory, splitext(coco_image_filename)[0])

        polygons = []
        if 'stage1' in ct_image.misc_info:
          polygons.extend(ct_image.misc_info['stage1']['polygons'])
        if 'stage2' in ct_image.misc_info:
          polygons.extend(ct_image.misc_info['stage2']['polygons'])
        
        for i, polygon in enumerate(polygons):
          crop_name = '{0}_{1}.jpg'.format(splitext(coco_image_filename)[0], i)
          crop_path = join(crop_sub_directory, crop_name)
          if exists(crop_path):
            obj, created = CocoTextInstance.objects.get_or_create(
              id='{}-{:03d}'.format(ct_image.id, i),
              image=ct_image,
              polygon=polygon,
              text=None,
              language=None,
              legibility=None,
              text_class=None,
              stage_2=True,
            )

  def create_contents(self):
    project = Project.objects.get(name='TextAnnotation')
    for ct_instance in tqdm(CocoTextInstance.objects.filter(stage_2=True)):
      Content.objects.get_or_create(
        text_instance=ct_instance,
        project=project,
        groundtruth_text=None,
        sentinel=False,
        consensus=None,
        status='U')

  def import_aster_recognition_results(self, pre_annotation_path):
    """Import recognition results produced by a recognizer named ASTER."""
    with open(pre_annotation_path, 'r') as f:
      preannotations = f.read()

    project = Project.objects.get(name='TextAnnotation')
    project_worker, _ = ProjectWorker.objects.get_or_create(
      mturk_worker=None,
      project=project,
      nickname='aster'
    )

    created_response_count = 0
    existing_response_count = 0

    regex = r"crops\/COCO_train2014_(\d+)\/COCO_train2014_(\d+)_(\d+)\.jpg (.+)$"
    matches = re.finditer(regex, preannotations, re.MULTILINE)
    for match in tqdm(matches):
      id1, id2 = match.group(1), match.group(2)
      assert(id1 == id2)
      image_id = int(id1)
      instance_index = int(match.group(3))
      annotation = match.group(4)

      ct_instance_id = '{}-{:03d}'.format(image_id, instance_index)
      try:
        ct_instance = CocoTextInstance.objects.get(id=ct_instance_id)
      except CocoTextInstance.DoesNotExist:
        logging.warning('Text instance {} not found'.format(ct_instance_id))
        continue

      content = ct_instance.textannot_content
      _, created = Response.objects.get_or_create(
        submission=None,
        content=content,
        project_worker=project_worker,
        text=annotation)

      if created:
        created_response_count += 1
      else:
        existing_response_count += 1

    print('Created {} responses, skipped {} responses'.format(created_response_count, existing_response_count))