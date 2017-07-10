from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from common.models import MturkHit
from common.utils import polygon_center


def get_task_data(request, hit_id):
    task = MturkHit.objects.get(id=hit_id).polyannot_task
    image_id = task.image.id
    image_url = settings.COCOTEXT_IMAGE_URL_TEMPLATE.format(image_id)

    task_data = {
        'imageId': image_id,
        'imageUrl': image_url,
        'staticPolygons': [],
        'hints': []
    }

    for c in task.contents.filter(type='ST'):
        task_data['staticPolygons'].append(c.text_instance.polygon)

    for c in task.contents.filter(type='HI'):
        hint_pos = polygon_center(c.text_instance.polygon)
        task_data['hints'].append(hint_pos)

    return JsonResponse(task_data)
