"""
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Unit Testing File
* Location : /mainsite/popclick/urls.py
"""
from django.test import TestCase
from popclick.models import *
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
import socket
import unittest
import json
import requests
# Test 1, profile creation

def getBaseURL():
	try:
	    HOSTNAME = socket.gethostname()
	except:
	    HOSTNAME = 'localhost'
	return HOSTNAME

class ProfileCreationTest(TestCase):
	def setUp(self):
		self.baseURI = "http://localhost:8000"
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_validate = "/popclick/api/validprofile/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"

	def test_details(self):
		profile = json.dumps( {"logtime":"2017-04-16 18:07","age":"5","gender":"Male","interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		# response = self.client.post(self.baseURI+self.uri_creation, profile, content_type="application/json")
		# factory = APIRequestFactory()
		r = requests.post(self.baseURI+self.uri_creation, profile)

		# request = factory.post(self.baseURI+self.uri_creation, profile, content_type="application/json")
		self.assertTrue(len(json.loads(r.content.decode('utf-8'))['profile']) == 20)