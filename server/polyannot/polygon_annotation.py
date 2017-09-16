import json
import codecs

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from common.models import MturkHit, MturkWorker, CocoTextImage, CocoTextInstance
from common.utils import polygon_center
from polyannot.models import Submission


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


def get_annotations_by_worker_id(request, worker_id, max_num=200):
    worker = MturkWorker.objects.get(id=worker_id).polyannot_worker
    submissions = worker.submissions

    imagesList = []

    for submission in submissions.filter(admin_mark='U')[:max_num]:
        image_id = submission.task.image.id
        annotations = []
        for response in submission.responses.all():
            polygon = response.text_instance.polygon
            annotations.append({'polygon': polygon})

        imagesList.append({
            'submissionId': submission.id,
            'imageId': image_id,
            'annotations': annotations,
            'adminMark': submission.admin_mark,
        })

    # sort image list by image id
    sortedLmagesList = sorted(imagesList, key=lambda item: int(item['imageId']))

    jsonResponse = {
        'workerId': worker.id,
        'imagesList': sortedLmagesList
    }

    return JsonResponse(jsonResponse)


def get_unverified_annotations(request, max_num=200):
    images_list = []
    unverified_submissions = Submission.objects.filter(admin_mark='U')[:max_num]

    for submission in unverified_submissions:
        image_id = submission.task.image.id
        annotations = []
        for response in submission.responses.all():
            polygon = response.text_instance.polygon
            annotations.append({'polygon': polygon})

        images_list.append({
            'submissionId': submission.id,
            'imageId': image_id,
            'annotations': annotations,
            'adminMark': submission.admin_mark,
        })

    print('Num of unverified: {}'.format(len(images_list)))
    
    # sort image list by image id
    # sorted_images_list = sorted(images_list, key=lambda item: int(item['imageId']))[:max_num]

    jsonResponse = {
        'imagesList': images_list
    }
    return JsonResponse(jsonResponse)


def get_annotations_by_image_ids(request, image_ids_str, include_v1=False):
    raise NotImplementedError('Have bugs. Do not use')
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
            'annotations': annotations,
            'adminMark': 'U' # FIXME
        })
    jsonResponse = {'imagesList': imagesList}
    return JsonResponse(jsonResponse)


@csrf_exempt
def set_admin_marks(request):
    marks = json.loads(codecs.decode(request.body))

    for key, value in marks.items():
        submission = Submission.objects.get(id=int(key))
        submission.admin_mark = value
        submission.save()

    return JsonResponse({})
