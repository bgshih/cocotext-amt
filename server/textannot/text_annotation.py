import os
from urllib.parse import urlparse, parse_qs

from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit, MturkWorker
from textannot.models import Task, Response


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


# viewer functions
def get_responses(request, url, max_length=100):
    print('url: ' + url)
    query_params = parse_qs(urlparse(url).query)
    print('query_params: ' + query_params)
    if 'worker' in query_params:
        worker_id = query_params['worker']
        project_worker = MturkWorker.objects.get(id=worker_id).textannot_worker
        responses = project_worker.responses
    else:
        responses = Response.objects.all()
    
    if 'sort' in query_params:
        if query_params['sort'] == 'recentfirst':
            responses = responses.order_by('-added')

    print(responses.count())
    print(responses[0])

    json_response = []
    for response in responses[:max_length]:
        text_instance_id = response.content.text_instance.id
        project_worker = str(response.project_worker)
        text = response.text
        illegible = response.illegible
        unknownLanguage = response.unknownLanguage
        json_response.append({
            'textInstanceId': text_instance_id,
            'worker': project_worker,
            'text': text,
            'illegible': illegible,
            'unknownLanguage': unknownLanguage
        })
    return JsonResponse(json_response)
