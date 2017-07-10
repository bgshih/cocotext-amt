from django.conf.urls import url

from polyannot import polygon_annotation

urlpatterns = [
    url(r'^task/(.+)/$', polygon_annotation.get_task_data),
    # for internal use
    # url(r'^_image/(.+)/$', polygon_annotation.get_image),
]
