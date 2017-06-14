from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit


def get_task_data(request, hit_id):
    task = MturkHit.objects.get(id=hit_id).task

    task_data = {
        'type': 'PolygonVerification',
        'contents': []
    }

    print(task.contents.all())

    for content in task.contents.all():
        text_instance = content.text_instance
        task_data['contents'].append({
            'id': text_instance.id,
            'verification': content.text_instance.polygon_verification
        })
    
    return JsonResponse(task_data)
