from django.conf.urls import url

from api import text_instance, polygon_annotation, polygon_verification

urlpatterns = [
    url(r'^polyannot/(.+)/$', polygon_annotation.get_task_data),
    url(r'^polyverif/(.+)/$', polygon_verification.get_task_data),
    url(r'^textins/(.+)/crop/$', text_instance.get_text_instance_crop),
    url(r'^textins/(.+)/crop/polygon/$', text_instance.get_text_instance_polygon_in_crop)
]
