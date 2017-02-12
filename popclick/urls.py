from django.conf.urls import url

from . import views

app_name = 'popclick'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/create/$', views.create_profile, name='create_profile'),
    url(r'^profiles/$', views.profiles, name='profiles'),
    url(r'^api/get/(?P<token>[a-zA-Z0-9]+)/$', views.get_initial_auth, name='auth'),
    url(r'^api/add/(?P<token>[a-zA-Z0-9]+)/$', views.populate_selectable, name='populate')
]