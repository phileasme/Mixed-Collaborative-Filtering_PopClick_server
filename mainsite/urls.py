"""mainsite URL Configuration
@provided by default
* Location : /mainsite/mainsite/urls.py
"""
from django.conf.urls import include, url
from django.contrib import admin
# URL Patterns required to use the popclick application
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^popclick/',include('popclick.urls', namespace="popclick")),
    url(r'^',include('popclick.urls', namespace="popclick"))
]
