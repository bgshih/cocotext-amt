from functools import partial

from django.conf.urls import url

from polyannot import polygon_annotation

urlpatterns = [
    url(r'^task/(.+)/$', polygon_annotation.get_task_data),
    # for internal use
    url(r'^_annotations/by_image_ids/(.+)/$', polygon_annotation.get_annotations_by_image_ids),
    url(r'^_annotations/by_worker_id/(\w+)/$', polygon_annotation.get_annotations_by_worker_id),
    url(r'^_annotations/by_worker_id/(\w+)/unverified/$',
        partial(polygon_annotation.get_annotations_by_worker_id, only_unverified=True)),
    url(r'^_annotations/unverified/$', polygon_annotation.get_unverified_annotations),
    url(r'^_annotations/set_admin_marks/$', polygon_annotation.set_admin_marks),
    url(r'^_annotations/set_user_marks/$', polygon_annotation.set_user_marks),
]
