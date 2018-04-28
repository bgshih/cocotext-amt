import os

from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit
from textannot.models import Task


def get_task_data(request, hit_id):
    try:
      task = MturkHit.objects.get(id=hit_id).textannot_task
      text_instances = [content.text_instance.id for content in task.contents.all()]
      print(text_instances)
      task_data = {
          'type': 'TextAnnotation',
          'textInstances': text_instances,
      }
      return JsonResponse(task_data)
    except Task.DoesNotExist:
      task_data = {
          'type': 'TextAnnotation',
          'textInstances': [],
      }
      return JsonResponse(task_data)
    except MturkHit.DoesNotExist:
      return get_example_task_data(request, hit_id)


def get_example_task_data(request, hit_id):
    task_data = {
        'type': 'TextAnnotation',
        'textInstances': [
          '64-000', '64-001', '64-001', '64-000', '64-001',
          '64-001', '64-000', '64-001', '64-001', '64-000',
          '64-001', '64-001',
        ]
    }
    return JsonResponse(task_data)


def get_crop(request, text_instance):
    """DO NOT USE THIS IN PRODUCTION"""
    DATA_ROOT = '../data/crops'

    image_id, instance_index = (int(s) for s in text_instance.split('-'))
    image_name = 'COCO_train2014_{:012d}'.format(image_id)
    crop_rel_path = '{0}/{0}_{1}.jpg'.format(image_name, instance_index)
    
    try:
        image_path = os.path.join(DATA_ROOT, crop_rel_path)
        return FileResponse(open(image_path, 'rb'))
        # with open(image_path, 'rb') as f:
        #     response = HttpResponse(f.read(), content_type="image/jpeg")
        #     return response
    except IOError:
        red = Image.new('RGBA', (1, 1), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response
