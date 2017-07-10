from django.conf.urls import url

from polyverif import polygon_verification

urlpatterns = [
    url(r'^task/(.+)/$', polygon_verification.get_task_data),
    # for internal use
    url(r'^_content/(.+)/$', polygon_verification.get_content),
    url(r'^_response/(.+)/$', polygon_verification.get_response)
]
