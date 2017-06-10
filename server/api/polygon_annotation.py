from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import MturkHit
# PolygonAnnotationTask

COCO_IMAGE_URL_TEMPLATE = 'https://s3.amazonaws.com/cocotext-images/train2014/COCO_train2014_%012d.jpg'

def get_task_data(request, hit_id):
    """
    Respond to client request with task data.
    """
    try:
        hit = MturkHit.objects.get(hit_id=hit_id)
        task = hit.text_region_task
        image_url = COCO_IMAGE_URL_TEMPLATE % int(task.coco_image_id)
        existing_polygons = task.existing_annot
        task_data = {
            'imageUrl': image_url,
            'hints': task.hints,
            'existingPolygons': existing_polygons,
        }
        return JsonResponse(task_data)
    except ObjectDoesNotExist:
        return JsonResponse({})
