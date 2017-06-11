import math
from os.path import join
import numpy as np
from PIL import Image

from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from common.models import CocoTextInstance


def _polygon_bbox(polygon):
    xs = [point['x'] for point in polygon]
    ys = [point['y'] for point in polygon]
    xmin = min(xs)
    xmax = max(xs)
    ymin = min(ys)
    ymax = max(ys)
    return ( xmin, ymin, xmax, ymax )


def _crop_image(image, crop_bbox):
    xmin, ymin, xmax, ymax = crop_bbox
    image_width, image_height = image.size
    crop_width = xmax - xmin
    crop_height = ymax - ymin
    im = np.asarray(image)
    crop = np.zeros((crop_height, crop_width, im.shape[2]), dtype=im.dtype)

    keep_x_in_crop = lambda x: max(0, min(crop_width-1, x))
    keep_y_in_crop = lambda y: max(0, min(crop_height-1, y))
    xmin_in_crop = keep_x_in_crop(-xmin)
    ymin_in_crop = keep_y_in_crop(-ymin)
    xmax_in_crop = keep_x_in_crop(image_width-1-xmin) + 1
    ymax_in_crop = keep_y_in_crop(image_height-1-ymin) + 1

    keep_x_in_image = lambda x: max(0, min(image_width-1, x))
    keep_y_in_image = lambda y: max(0, min(image_height-1, y))
    xmin_in_image = keep_x_in_image(xmin)
    ymin_in_image = keep_y_in_image(ymin)
    xmax_in_image = keep_x_in_image(xmax-1) + 1
    ymax_in_image = keep_y_in_image(ymax-1) + 1

    crop[ymin_in_crop:ymax_in_crop, xmin_in_crop:xmax_in_crop, :] = \
        im[ymin_in_image:ymax_in_image, xmin_in_image:xmax_in_image, :]
    return Image.fromarray(crop)


def _crop_bbox(polygon):
    """ Find the crop bbox and the relative polygon inside the crop """
    xmin, ymin, xmax, ymax = _polygon_bbox(polygon)
    width, height = xmax - xmin, ymax - ymin
    margin = math.ceil(math.sqrt(width * height) * settings.TEXT_INSTANCE_CROP_MARGIN_RATIO)
    crop_xmin = int(math.floor(xmin - margin))
    crop_ymin = int(math.floor(ymin - margin))
    crop_xmax = int(math.floor(xmax + margin)) + 1
    crop_ymax = int(math.floor(ymax + margin)) + 1

    relative_polygon = []
    for point in polygon:
        relative_polygon.append({
            'x': point['x'] - crop_xmin,
            'y': point['y'] - crop_ymin,
        })

    return (crop_xmin, crop_ymin, crop_xmax, crop_ymax), relative_polygon


def get_text_instance_crop(request, instance_id):
    try:
        # retrieve text instance
        text_instance = CocoTextInstance.objects.get(id=instance_id)
        
        # load image locally
        image_filename = text_instance.image.filename
        image_path = join(settings.LOCAL_COCO_IMAGE_DIR, image_filename)
        image = Image.open(image_path)

        # crop around polygon
        polygon = text_instance.polygon
        crop_bbox, _ = _crop_bbox(polygon)
        crop_image = _crop_image(image, crop_bbox)
    except (CocoTextInstance.DoesNotExist, IOError):
        crop_image = Image.new('RGBA', (1, 1), (0,0,0,0))

    response = HttpResponse(content_type='image/jpeg')
    crop_image.save(response, 'JPEG')
    return response


def get_text_instance_polygon_in_crop(request, instance_id):
    text_instance = CocoTextInstance.objects.get(id=instance_id)
    _, relative_polygon = _crop_bbox(text_instance.polygon)
    return JsonResponse({
        'relativePolygon': relative_polygon
    })
