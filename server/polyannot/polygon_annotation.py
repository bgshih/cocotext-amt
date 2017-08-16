from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from common.models import MturkHit, MturkWorker, CocoTextImage, CocoTextInstance
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


def get_annotations_by_worker_id(request, worker_id):
    worker = MturkWorker.objects.get(id=worker_id).polyannot_worker
    submissions = worker.submissions

    imagesList = []

    for submission in submissions.all():
        image_id = submission.task.image.id
        annotations = []
        for response in submission.responses.all():
            polygon = response.text_instance.polygon
            annotations.append({'polygon': polygon})

        imagesList.append({
            'imageId': image_id,
            'annotations': annotations
        })

    jsonResponse = {
        'workerId': worker.id,
        'imagesList': imagesList
    }

    return JsonResponse(jsonResponse)


def get_annotations_by_image_ids(request, image_ids_str, include_v1=False):
    image_ids = [id for id in image_ids_str.split(',')]

    imagesList = []
    for image_id in image_ids:
        image = CocoTextImage.objects.get(id=image_id)
        text_instances = image.text_instances.filter(from_v1=include_v1)
        annotations = []
        for text_instance in text_instances:
            annotations.append({'polygon': text_instance.polygon})
        imagesList.append({
            'imageId': image_id,
            'annotations': annotations
        })
    jsonResponse = {'imagesList': imagesList}
    return JsonResponse(jsonResponse)
