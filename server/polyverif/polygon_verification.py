from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit
from polyverif.models import Content, Response


def get_task_data(request, hit_id):
    task = MturkHit.objects.get(id=hit_id).polyverif_task

    task_data = {
        'type': 'PolygonVerification',
        'contents': [],
        'gtAnswers': {},
    }

    for content in task.contents.all():
        instance_id = content.text_instance.id
        task_data['contents'].append({
            'instanceId': instance_id,
            'verification': 'U'
        })

        if content.sentinel == True:
            task_data['gtAnswers'][instance_id] = content.gt_verification
    
    return JsonResponse(task_data)


def get_content(request, content_ids_str):
    """
    Given content id, respond content text instance id and consensus.
    This is for the internal content viewer tool.
    """
    contents = []
    content_ids = content_ids_str.split(',')

    for content_id in content_ids:
        content_id = int(content_id)
        content = Content.objects.get(id=content_id)
        instance_id = content.text_instance.id
        content_status = content.status

        content_data = {
            'id': instance_id,
            'verification': content.consensus or 'U'
        }

        contents.append(content_data)

    return JsonResponse({'contents': contents})


def get_response(request, response_ids_str):
    """
    Given response id, respond response text instance id and verification
    This is for the internal response viewer tool.
    """

    response_ids = response_ids_str.split(',')
    responses = []

    for response_id in response_ids:
        response = Response.objects.get(id=response_id)
        content = response.content
        instance_id = content.text_instance.id

        response_data = {
            'id': instance_id,
            'verification': response.verification
        }
        responses.append(response_data)

    return JsonResponse({'responses': responses})
