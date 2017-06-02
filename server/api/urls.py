from django.conf.urls import url

from . import polygon_annotation

urlpatterns = [
    url(r'^polygon-annotation/by-hit/(.+)/$', polygon_annotation.get_task_data),
]
