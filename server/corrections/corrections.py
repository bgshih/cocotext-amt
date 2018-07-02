import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from common.models import CocoTextInstance, CocoTextImage
from corrections.models import ImageCorrection, InstanceCorrection


@csrf_exempt
def save_correction(request):
    if request.method == 'POST':
        correction_json = json.loads(request.body.decode('utf8'))
        if 'instance_id' in correction_json:
            # save instance correction
            ct_instance = CocoTextInstance.objects.get(id=correction_json['instance_id'])
            InstanceCorrection.objects.get_or_create(
                ct_instance=ct_instance,
                correction=correction_json
            )
        elif 'image_id' in correction_json:
            ct_image = CocoTextImage.objects.get(id=str(correction_json['image_id']))
            ImageCorrection.objects.get_or_create(
                ct_image=ct_image,
            )
    return HttpResponse('OK')

