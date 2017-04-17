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
import json
import requests
from django.test import Client

 ######### ######### ######### ######### ######### ######### ########
 # Before running any test, the server must be running concurrently	#
 # Before running the tests using the recommendation live			#
 # Either type : curl -I https://salty-dusk-83190.herokuapp.com/	#
 #			     curl -I https://blooming-crag-27676.herokuapp.com/	#
 #				 or navigate to the urls listed above.				#
 ######### ######### ######### ######### ######### ######### ########

def getBaseURL():
	try:
	    HOSTNAME = socket.gethostname()
	except:
	    HOSTNAME = 'localhost'
	return HOSTNAME

class ProfileCreationTest(TestCase):
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_suggestion = "/api/suggestion/"

	def test_valid_profile_creation(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"5","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		profile_token = json.loads(r.content.decode('utf-8'))['profile']
		self.assertTrue(len(profile_token) == 20)

	def test_invalid_profile_interests(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"5","gender":"Male",
			"interests":["Social Awareness","Bad Interests","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'WRONG_INTERESTS')

	def test_invalid_profile_age(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"99900","gender":"Male",
			"interests":["Social Awareness","Literature","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'INVALID_AGE')

	def test_invalid_profile_gender(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"22","gender":"FAKE GENDER",
			"interests":["Social Awareness","Literature","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'INVALID_GENDER')

	def test_profile_authentication_and_validated(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"5","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		profile_token = json.loads(r.content.decode('utf-8'))['profile']
		self.assertTrue(Profile.objects.get(token=profile_token))
		auth_r = client.get(self.uri_auth+profile_token+'/')
		self.assertTrue(len(json.loads(auth_r.content.decode('utf-8'))['auth']) == 20)
		self.assertTrue(Profile.objects.get(token=profile_token).activated)

class ProfilePageobjectPopulate(TestCase):
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
	def test_pageobject_creation(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"5","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		profile_token = json.loads(r.content.decode('utf-8'))['profile']
		self.assertTrue(Profile.objects.get(token=profile_token))
		auth_r = client.get(self.uri_auth+profile_token+'/')
		profile_auth = json.loads(auth_r.content.decode('utf-8'))['auth']
		pageobject_json = json.dumps( {"profile":[profile_auth,"2017-04-17 01:40"],"pageobject":["https://immense-bastion-46341.herokuapp.com/","https://pencils.com/","PENCILS","something","immense-bastion-46341.herokuapp.com","/"],"interaction":["create",1]} )
		pageobject_created_r = client.post(self.uri_add_selectable+profile_token+'/', content_type='application/json', data=pageobject_json)
		self.assertEqual(pageobject_created_r.status_code, 200)

	def page_one(auth):
		return json.dumps({"profile":auth,"pageobjects":[["https://immense-bastion-46341.herokuapp.com/",
		"https://www.football.com/","FOOTBALL","html>body>div:eq(0)>div:eq(0)>a"],
		["https://immense-bastion-46341.herokuapp.com/","https://www.bloomberg.com/quote/DXY:CUR","DOLLARS",
		"html>body>div:eq(0)>div:eq(1)>a"],["https://immense-bastion-46341.herokuapp.com/","https://pencils.com/",
		"PENCILS","html>body>div:eq(0)>div:eq(2)>a"],["https://immense-bastion-46341.herokuapp.com/",
		"http://www.multiplication.com/","MULTIPLICATIONS","html>body>div:eq(1)>div:eq(0)>a"],
		["https://immense-bastion-46341.herokuapp.com/","https://harrypotter.com/","HARRY POTTER",
		"html>body>div:eq(1)>div:eq(1)>a"],["https://immense-bastion-46341.herokuapp.com/",
		"https://www.ft.com/?edition=uk","FINANCIAL TIMES","html>body>div:eq(1)>div:eq(2)>a"],
		["https://immense-bastion-46341.herokuapp.com/","","Close","html>body>div:eq(3)>div:eq(0)>a"]]})
class RecommendationUserItem(TestCase):
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"

		bob_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"18","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		bob_twin_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"18","gender":"Male",
			"interests":["Literature","Movies & Theatre","Craft"],"signed":1})
		
		bob_r = client.post(self.uri_creation, content_type='application/json', data=bob_json)
		bob_twin_r = client.post(self.uri_creation, content_type='application/json', data=bob_twin_json)
		
		bob_profile_token = json.loads(bob_r.content.decode('utf-8'))['profile']
		bob_twin_profile_token = json.loads(bob_twin_r.content.decode('utf-8'))['profile']
		
		self.bob_profile = Profile.objects.get(token=bob_profile_token)
		self.bob_twin1_profile = Profile.objects.get(token=bob_twin_profile_token)
		
		client.get(self.uri_auth+bob_profile_token+'/')
		client.get(self.uri_auth+bob_twin_profile_token+'/')
	# def test_recommendation_order(self):
class NeuralNetwork(TestCase):
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"