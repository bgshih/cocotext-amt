from django.conf.urls import url

from polyannot import polygon_annotation

urlpatterns = [
    url(r'^task/(.+)/$', polygon_annotation.get_task_data),
    # for internal use
    url(r'^_annotations/by_image_ids/(.+)/$', polygon_annotation.get_annotations_by_image_ids),
    url(r'^_annotations/by_worker_id/(.+)/$', polygon_annotation.get_annotations_by_worker_id),
]
