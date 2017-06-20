from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit


def get_task_data(request, hit_id):
    task = MturkHit.objects.get(id=hit_id).task

    task_data = {
        'type': 'PolygonVerification',
        'contents': [],
        'gtAnswers': {},
    }

    for content in task.contents.all():
        text_instance = content.text_instance
        instance_id = text_instance.id

        task_data['contents'].append({
            'id': instance_id,
            'verification': 'U'
        })

        print(content.sentinel)
        if content.sentinel == True:
            task_data['gtAnswers'][instance_id] = content.gt_verification
    
    return JsonResponse(task_data)
