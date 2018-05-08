from django.conf.urls import url

from textannot import text_annotation

urlpatterns = [
    url(r'^task/(.+)/$', text_annotation.get_task_data),
    url(r'^crop/(.+)$', text_annotation.get_crop),
    url(r'^response/(.*)$', text_annotation.get_responses),
]
