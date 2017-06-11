from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from common.models import MturkHit
from polyverif.models import PolygonVerificationTask


def get_task_data(request, hit_id):
    task = MturkHit.objects.get(id=hit_id).polyverif_task
    verif_instances = task.verification_instances.all()

    task_data = {
        'type': 'PolygonVerification',
        'instances': []
    }
    for verif_instance in verif_instances:
        text_instance = verif_instance.text_instance
        task_data['instances'].append({
            'id': text_instance.id,
            'status': verif_instance.verification_status()
        })
    return JsonResponse(task_data)
