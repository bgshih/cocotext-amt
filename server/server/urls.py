"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from common import text_instance
from corrections import corrections

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^textins/(.+)/crop/$', text_instance.get_text_instance_crop),
    url(r'^textins/(.+)/crop/polygon/$', text_instance.get_text_instance_polygon_in_crop),
    url(r'^polyverif/', include('polyverif.urls')),
    url(r'^polyannot/', include('polyannot.urls')),
    url(r'^textannot/', include('textannot.urls')),
    url(r'^corrections/', corrections.save_correction),
]
