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
    image = task.image
    image_id = image.id
    image_url = settings.COCOTEXT_IMAGE_URL_TEMPLATE.format(image_id)

    staticPolygons = []
    if image.misc_info is not None and 'stage1' in image.misc_info:
        staticPolygons = image.misc_info['stage1']['polygons']

    print(staticPolygons)

    task_data = {
        'imageId': image_id,
        'imageUrl': image_url,
        'staticPolygons': staticPolygons,
        'hints': []
    }

    # for c in task.contents.filter(type='ST'):
    #     task_data['staticPolygons'].append(c.text_instance.polygon)

    # for c in task.contents.filter(type='HI'):
    #     hint_pos = polygon_center(c.text_instance.polygon)
    #     task_data['hints'].append(hint_pos)

    return JsonResponse(task_data)


def get_annotations_by_worker_id(request, worker_id, only_unverified=False, max_num=200, recent_first=True):
    worker = MturkWorker.objects.get(id=worker_id).polyannot_worker

    submissions = worker.submissions.order_by('-added')
    if only_unverified:
        submissions = submissions.filter(admin_mark='U')
    # if recent_first:
    #     submissions = submissions.order_by('-added')
    # else:
    #     submissions = submissions.all()

    imagesList = []

    for submission in submissions[:max_num]:
        image_id = submission.task.image.id
        annotations = []
        for response in submission.responses.all():
            polygon = response.text_instance.polygon
            annotations.append({'polygon': polygon})

        hasRemainingText = submission.answer['hasRemainingText']

        previous_annotations = submission.task.image.misc_info['stage1']

        imagesList.append({
            'submissionId': submission.id,
            'imageId': image_id,
            'annotations': annotations,
            'adminMark': submission.admin_mark,
            'hasRemainingText': hasRemainingText,
            'previousAnnotations': previous_annotations
        })

    # sort image list by image id
    sortedLmagesList = sorted(imagesList, key=lambda item: int(item['imageId']))

    jsonResponse = {
        'workerId': worker.id,
        'imagesList': sortedLmagesList
    }

    return JsonResponse(jsonResponse)


def get_unverified_annotations_for_worker_52(request, max_num=50):
    images_list = []
    unverified_submissions = \
        Submission.objects.filter(admin_mark='U').exclude(project_worker=52).order_by('-added')

    selected_submission_list = []
    for submission in unverified_submissions:
        if submission.misc_info is None or \
           'user_marks' not in submission.misc_info:
            selected_submission_list.append(submission)
        if len(selected_submission_list) >= max_num:
            break

    for submission in selected_submission_list:
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


@csrf_exempt
def set_user_marks(request):
    submission_json = json.loads(codecs.decode(request.body))
    user_marks = submission_json['userMarks']
    user_id = submission_json['userId']

    for key, value in user_marks.items():
        submission = Submission.objects.get(id=int(key))
        misc_info = submission.misc_info
        if misc_info is None:
            misc_info = {}
        if 'user_marks' not in misc_info:
            misc_info['user_marks'] = {}
        misc_info['user_marks'][user_id] = value
        submission.misc_info = misc_info
        submission.save()
    return JsonResponse({})
