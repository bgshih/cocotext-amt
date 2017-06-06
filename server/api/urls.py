from django.conf.urls import url

from . import polygon_annotation

urlpatterns = [
    url(r'^polyannot/task/by-hit/(.+)/$', polygon_annotation.get_task_data),
    url(r'^polyverif/task/by-hit/(.+)/$', polygon_verification.get_task_data),
]
