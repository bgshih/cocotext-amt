from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from api.models import MturkHit, PolygonVerificationTask


def get_task_data(request, hit_id):
    hit = MturkHit.objects.get(id=hit_id)
    polyverif_task = hit.polygon_verification_task
    verif_instances = polyverif_task.verification_instances.all()

    task_data = {
        'type': 'PolygonVerification',
        'instances': []
    }
    for verif_instance in verif_instances:
        text_instance = verif_instance.text_instance
        image_url = text_instance.image.filename # TODO
        polygon = text_instance.polygon
        task_data['instances'].append({
            'id': text_instance.id,
            'status': verif_instance.text_instance.polygon_verification
        })
    return JsonResponse(task_data)


def post_answer(request, answer):
    pass
