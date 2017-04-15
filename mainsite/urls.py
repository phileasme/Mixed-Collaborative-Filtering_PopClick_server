"""mainsite URL Configuration

@provided by default
"""
from django.conf.urls import include, url
from django.contrib import admin
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^popclick/',include('popclick.urls', namespace="popclick")),
]
