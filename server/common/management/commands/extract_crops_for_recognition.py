from os.path import join, splitext, exists
from os import mkdir
import json
import math

import numpy as np
from tqdm import tqdm
from PIL import Image

from django.core.management.base import BaseCommand, CommandError

from common.models import CocoTextImage, CocoTextInstance


class Command(BaseCommand):
  help = 'Extract crops'

  def add_arguments(self, parser):
    parser.add_argument(
      '--coco_image_directory',
      action='store',
      dest='coco_image_directory',
      default='',
      type=str,
      help='Directory of MSCOCO images',
    )
    parser.add_argument(
      '--crop_save_directory',
      action='store',
      dest='crop_save_directory',
      default='',
      type=str,
      help='Directory for saving crops',
    )

  def handle(self, *args, **options):
    # self.misc_info_statistics()
    self.crop_images(options['coco_image_directory'], options['crop_save_directory'])

  def misc_info_statistics(self):
    count_has_misc_info = 0
    count_has_stage1_info = 0
    count_has_stage2_info = 0
    count_has_more_info = 0
    count_has_stage2_but_no_stage1_info = 0

    for image in tqdm(CocoTextImage.objects.all()):
      if image.misc_info is not None:
        count_has_misc_info += 1

        misc_info = image.misc_info
        if 'stage1' in misc_info:
          count_has_stage1_info += 1
        if 'stage2' in misc_info:
          count_has_stage2_info += 1

        if 'stage2' in misc_info and 'stage1' not in misc_info:
          count_has_stage2_but_no_stage1_info += 1
        
        if len(misc_info.keys()) > 2:
          count_has_more_info += 1

    print('count_has_misc_info = {}'.format(count_has_misc_info))
    print('count_has_stage1_info = {}'.format(count_has_stage1_info))
    print('count_has_stage2_info = {}'.format(count_has_stage2_info))
    print('count_has_more_info = {}'.format(count_has_more_info))
    print('count_has_stage2_but_no_stage1_info = {}'.format(count_has_stage2_but_no_stage1_info))


  def crop_images(self, coco_image_directory, crop_save_directory):

    def _polygon_bounding_box(polygon):
      xs = [point['x'] for point in polygon]
      ys = [point['y'] for point in polygon]
      xmin, xmax = min(xs), max(xs)
      ymin, ymax = min(ys), max(ys)
      return (xmin, xmax, ymin, ymax)
    
    def _expand_bbox(bbox, padding_ratio=0.15):
      xmin, xmax, ymin, ymax = bbox
      padding = math.sqrt((xmax - xmin) * (ymax - ymin)) * padding_ratio
      new_xmin = xmin - padding
      new_xmax = xmax + padding
      new_ymin = ymin - padding
      new_ymax = ymax + padding
      return (new_xmin, new_xmax, new_ymin, new_ymax)
    
    def _box_to_coordinate(bbox, image_width, image_height):
      def _constrain_to_border(x, y):
        x = max(0, min(image_width-1, x))
        y = max(0, min(image_height-1, y))
        return int(x), int(y)
      xmin, xmax, ymin, ymax = bbox
      xmin, ymin = _constrain_to_border(xmin, ymin)
      xmax, ymax = _constrain_to_border(xmax, ymax)
      valid = (xmax - xmin) > 0 and (ymax - ymin) > 0
      return (xmin, ymin, xmax, ymax), valid
    
    def _check_polygon_validity(polygon):
      return len(polygon) >= 3

    num_instances = 0

    for ct_image in tqdm(CocoTextImage.objects.all()):
      if ct_image.misc_info is not None:

        # load COCO image
        coco_image_filename = ct_image.filename
        coco_image_path = join(coco_image_directory, coco_image_filename)
        image = Image.open(coco_image_path)

        assert image.width == ct_image.width and image.height == ct_image.height

        polygons = []
        if 'stage1' in ct_image.misc_info:
          polygons.extend(ct_image.misc_info['stage1']['polygons'])
        if 'stage2' in ct_image.misc_info:
          polygons.extend(ct_image.misc_info['stage2']['polygons'])

        crop_sub_directory = join(crop_save_directory, splitext(coco_image_filename)[0])
        if len(polygons) > 0 and not exists(crop_sub_directory):
          mkdir(crop_sub_directory)

        for i, polygon in enumerate(polygons):
          valid_polygon = _check_polygon_validity(polygon)
          if valid_polygon:
            bbox = _polygon_bounding_box(polygon)
            expanded_bbox = _expand_bbox(bbox, padding_ratio=0.15)
            crop_coordinates, valid_bbox = _box_to_coordinate(expanded_bbox, image.width, image.height)
            if valid_bbox:
              crop = image.crop(crop_coordinates)
              crop_name = '{0}_{1}.jpg'.format(splitext(coco_image_filename)[0], i)
              crop.save(join(crop_sub_directory, crop_name))

        num_instances += len(polygons)

    print('Cropped {} text instances'.format(num_instances))
