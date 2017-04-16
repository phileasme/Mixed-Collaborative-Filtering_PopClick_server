""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Location : /mainsite/popclick/urls.py
"""
from django.conf.urls import url

from . import views

"""
Urls associated to Popclick
"""
app_name = 'popclick'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/create/$', views.create_profile, name='create_profile'),
    url(r'^api/get/(?P<token>[a-zA-Z0-9]+)/$', views.get_initial_auth, name='auth'),
    url(r'^api/add/(?P<token>[a-zA-Z0-9]+)/$', views.populate_selectable, name='populate'),
    url(r'^api/suggestion/(?P<token>[a-zA-Z0-9]+)/$', views.get_suggestion, name='suggestion'),
    url(r'^api/keygen/(?P<key>[a-zA-Z0-9]+)/$', views.keygen, name='genkey'),
    url(r'^api/validprofile/(?P<token>[a-zA-Z0-9]+)/$', views.valid_profile, name='valid_profil')
]