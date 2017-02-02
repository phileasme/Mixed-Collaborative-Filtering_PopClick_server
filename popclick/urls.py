from django.conf.urls import url

from . import views

app_name = 'popclick'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/create/$', views.create_profile, name='create_profile'),
    url(r'^profiles/$', views.profiles, name='profiles')
]