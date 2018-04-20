import os

from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit
from polyverif.models import Content, Response


def get_task_data(request, hit_id):
    return get_example_task_data(request, hit_id)

    # task = MturkHit.objects.get(id=hit_id).textannot_task
    # task_data = {
    #     'type': 'TextAnnotation',
    #     'crop_names': task.crop_names,
    # }
    # return JsonResponse(task_data)


def get_example_task_data(request, hit_id):
    task_data = {
        'type': 'TextAnnotation',
        'crop_names': [
          'COCO_train2014_000000000064/COCO_train2014_000000000064_0.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_0.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_0.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_0.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
          'COCO_train2014_000000000064/COCO_train2014_000000000064_1.jpg',
        ]
    }
    return JsonResponse(task_data)


def get_crop(request, image_name):
    """DO NOT USE THIS IN PRODUCTION"""
    DATA_ROOT = '../data/crops'
    
    try:
        image_path = os.path.join(DATA_ROOT, image_name)
        return FileResponse(open(image_path, 'rb'))
        # with open(image_path, 'rb') as f:
        #     response = HttpResponse(f.read(), content_type="image/jpeg")
        #     return response
    except IOError:
        red = Image.new('RGBA', (1, 1), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response
