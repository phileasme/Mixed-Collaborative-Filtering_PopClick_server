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

 ######### ######### ######### ######### ######### ######### ######## ###
 # Before running any test, the server must be running concurrently		#
 # Before running the tests using the recommendation live				#
 # Either type : curl -I https://immense-bastion-46341.herokuapp.com/ 	#
 #			     curl -I https://blooming-crag-27676.herokuapp.com/		#
 #				 or navigate to the urls listed above.					#
 ######### ######### ######### ######### ######### ######### ######## ###


#  Website 1 web page, page specially made for testing purposes
# https://immense-bastion-46341.herokuapp.com/ 
# 
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

def page_one_objects(auth,item):
	object_list =[
	{"profile":[auth,"2017-04-17 03:00"],
	"pageobject":["https://immense-bastion-46341.herokuapp.com/",
	"https://www.football.com/","FOOTBALL","something",
	"immense-bastion-46341.herokuapp.com","/"],
	"interaction":["create",1]},
	{"profile":[auth,"2017-04-17 03:02"],
	"pageobject":["https://immense-bastion-46341.herokuapp.com/",
	"https://www.bloomberg.com/quote/DXY:CUR","DOLLARS","something",
	"immense-bastion-46341.herokuapp.com","/"],
	"interaction":["create",1]}
	]
	return json.dumps(object_list[item])
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
		pageobject_json = page_one_objects(profile_auth, 0)
		pageobject_created_r = client.post(self.uri_add_selectable+profile_token+'/',
		 content_type='application/json', data=pageobject_json)
		self.assertEqual(pageobject_created_r.status_code, 200)

class GetRecommendation(TestCase):
	def setUp(self):
		client = Client()
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"

		bob_the_socialaware_twin_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"18","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		bob_the_artist_twin_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"18","gender":"Male",
			"interests":["Literature","Movies & Theatre","Craft"],"signed":1})
		alice_the_artist_json = json.dumps( {"logtime":"2017-04-16 18:07","age":"18","gender":"Female",
			"interests":["Literature","Arts","Craft"],"signed":1})
		
		bob_the_socialaware_twin_r = client.post(self.uri_creation, content_type='application/json', data=bob_the_socialaware_twin_json)
		bob_the_artist_twin_r = client.post(self.uri_creation, content_type='application/json', data=bob_the_artist_twin_json)
		alice_the_artist_r = client.post(self.uri_creation, content_type='application/json', data=alice_the_artist_json)

		bob_the_socialaware_twin_profile_token = json.loads(bob_the_socialaware_twin_r.content.decode('utf-8'))['profile']
		bob_the_artist_twin_profile_token = json.loads(bob_the_artist_twin_r.content.decode('utf-8'))['profile']
		alice_the_artist_profile_token = json.loads(alice_the_artist_r.content.decode('utf-8'))['profile']
		self.bob_the_socialaware_twin_profile = Profile.objects.get(token=bob_the_socialaware_twin_profile_token)
		self.bob_the_artist_twin_profile = Profile.objects.get(token=bob_the_artist_twin_profile_token)
		self.alice_the_artist_profile = Profile.objects.get(token=alice_the_artist_profile_token)
		self.bob_the_socialaware_twin_auth = json.loads(client.get(self.uri_auth+bob_the_socialaware_twin_profile_token+'/').content.decode('utf-8'))['auth']
		self.bob_the_artist_twin_auth = json.loads(client.get(self.uri_auth+bob_the_artist_twin_profile_token+'/').content.decode('utf-8'))['auth']
		self.alice_the_artist_auth = json.loads(client.get(self.uri_auth+alice_the_artist_profile_token+'/').content.decode('utf-8'))['auth']

	def test_get_no_suggestion(self):
		client = Client()
		bob_the_socialaware_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_socialaware_twin_profile.token+'/', 
			content_type='application/json', data=page_one(self.bob_the_socialaware_twin_auth))
		contx = json.loads(bob_the_socialaware_twin_page1_suggestion.content.decode('utf-8'))['recommendation']
		self.assertEqual(contx, 'No known objects')

	def test_get_suggestion(self):
		client = Client()
		client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/', 
			content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))

		bob_the_artist_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_artist_twin_profile.token+'/', 
			content_type='application/json', data=page_one(self.bob_the_artist_twin_auth))
		contx = json.loads(bob_the_artist_twin_page1_suggestion.content.decode('utf-8'))['recommendation']
		# First element of the given list
		self.assertEqual(contx, '[0]')

	def test_profile_browsing_error(self):
		client = Client()
		client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))
		# Returning to the original webpage in less than 5 seconds
		bob_the_socialaware_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_socialaware_twin_profile.token+'/',
		 content_type='application/json', data=page_one(self.bob_the_socialaware_twin_auth))
		
		bob_the_artist_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_artist_twin_profile.token+'/',
		 content_type='application/json', data=page_one(self.bob_the_artist_twin_auth))
		contx = json.loads(bob_the_artist_twin_page1_suggestion.content.decode('utf-8'))['recommendation']

		self.assertEqual(contx, 'No known objects')

class NeuralNetwork(TestCase):
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"
