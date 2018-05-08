from django.conf.urls import url

from textannot import text_annotation

urlpatterns = [
    url(r'^task/(.+)/$', text_annotation.get_task_data),
    url(r'^crop/(.+)$', text_annotation.get_crop),
    # url(r'^crop/(?P<imgname>.+)$', 'redirect_to', {'url': 'https://s3.amazonaws.com/cocotext/crops/%(imgname)'}),
    url(r'^_view/(.+)$', text_annotation.get_responses)
]
