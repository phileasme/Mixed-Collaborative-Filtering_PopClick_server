"""
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Unit Testing File
* Location : /mainsite/popclick/tests.py
"""
from django.test import TestCase
from popclick.models import *
from django.test import RequestFactory
import json
import requests
from django.test import Client
from time import sleep
from subprocess import call
import requests
import ast
# from django.test.runner import DiscoverRunner
from popclick.test_pages_and_objects import *

 ######### ######### ######### ######### ######### ######### ######## ## #
 # Before running any test, the server must be running concurrently:	 #
 #		python manage.py runserver	within python_server/mainsite		 #
 #																		 #
 # If testing on a real system is desired testing websites are available:#
 #				https://immense-bastion-46341.herokuapp.com/ 			 #
 #			    https://glacial-beyond-99420.herokuapp.com/	 			 #
 #				 	or navigate to the urls listed above,				 #
 #				(This is also necessary to produce a wakeup call.		 #
 ######### ######### ######### ######### ######### ######### ######## ###


class ProfileCreationTest(TestCase):
	"""
		Class that handles requests involved with the profiles
		
	"""
	def setUp(self):
		# different part uri's used for the queries
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_suggestion = "/api/suggestion/"

	def test_valid_profile_creation(self):
		# Creates a valid profile
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"5","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		profile_token = json.loads(r.content.decode('utf-8'))['profile']
		self.assertTrue(len(profile_token) == 20)

	def test_invalid_profile_interests(self):
		# Creates an invalid profile with as cause : interest
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"5","gender":"Male",
			"interests":["Social Awareness","Bad Interests","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'WRONG_INTERESTS')

	def test_invalid_profile_age(self):
		# Creates an invalid profile with as cause : age
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"99900","gender":"Male",
			"interests":["Social Awareness","Literature","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'INVALID_AGE')

	def test_invalid_profile_gender(self):
		# Creates an invalid profile with as cause : gender
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"22","gender":"FAKE GENDER",
			"interests":["Social Awareness","Literature","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		error_made = json.loads(r.content.decode('utf-8'))
		self.assertEqual(error_made['profile_error'], 'INVALID_GENDER')

	def test_profile_authentication_and_validated(self):
		# Valid profile , token request, auth, activate
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"5","gender":"Male",
			"interests":["Social Awareness","Movies & Theatre","Craft"],"signed":1})
		r = client.post(self.uri_creation, content_type='application/json', data=profile_json)
		profile_token = json.loads(r.content.decode('utf-8'))['profile']
		self.assertTrue(Profile.objects.get(token=profile_token))
		auth_r = client.get(self.uri_auth+profile_token+'/')
		self.assertTrue(len(json.loads(auth_r.content.decode('utf-8'))['auth']) == 20)
		self.assertTrue(Profile.objects.get(token=profile_token).activated)

class ProfilePageobjectPopulate(TestCase):
	"""
		Handles the population of pageobjects
	"""
	def setUp(self):
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
	# Creates a valid pageobject
	def test_pageobject_creation(self):
		client = Client()
		profile_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"5","gender":"Male",
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

class GetRecommendation_and_NeuralNetwork(TestCase):
	"""
		Tests the properties of the recommender engine as well as neural network
	"""
	def setUp(self):
		client = Client()
		self.uri_creation = "/popclick/api/create/"
		self.uri_auth = "/popclick/api/get/"
		self.uri_add_selectable = "/api/add/"
		self.uri_suggestion = "/api/suggestion/"
		# Fictional profiles
		bob_the_socialaware_twin_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"18","gender":"Male",
			"interests":["Social Awareness","Travel","News & Media"],"signed":1})
		bob_the_artist_twin_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"18","gender":"Male",
			"interests":["Literature","Movies & Theatre","Craft"],"signed":1})
		alice_the_artist_json = json.dumps( {"logtime":"2017-02-10 10:00","age":"18","gender":"Female",
			"interests":["Literature","Arts","Craft"],"signed":1})
		# Creates the profiles receive token
		bob_the_socialaware_twin_r = client.post(self.uri_creation, content_type='application/json', data=bob_the_socialaware_twin_json)
		bob_the_artist_twin_r = client.post(self.uri_creation, content_type='application/json', data=bob_the_artist_twin_json)
		alice_the_artist_r = client.post(self.uri_creation, content_type='application/json', data=alice_the_artist_json)
		# CONVERTS from json objects
		bob_the_socialaware_twin_profile_token = json.loads(bob_the_socialaware_twin_r.content.decode('utf-8'))['profile']
		bob_the_artist_twin_profile_token = json.loads(bob_the_artist_twin_r.content.decode('utf-8'))['profile']
		alice_the_artist_profile_token = json.loads(alice_the_artist_r.content.decode('utf-8'))['profile']
		# retreives objects
		self.bob_the_socialaware_twin_profile = Profile.objects.get(token=bob_the_socialaware_twin_profile_token)
		self.bob_the_artist_twin_profile = Profile.objects.get(token=bob_the_artist_twin_profile_token)
		self.alice_the_artist_profile = Profile.objects.get(token=alice_the_artist_profile_token)
		# authenticates the profiles
		self.bob_the_socialaware_twin_auth = json.loads(client.get(self.uri_auth+bob_the_socialaware_twin_profile_token+'/').content.decode('utf-8'))['auth']
		self.bob_the_artist_twin_auth = json.loads(client.get(self.uri_auth+bob_the_artist_twin_profile_token+'/').content.decode('utf-8'))['auth']
		self.alice_the_artist_auth = json.loads(client.get(self.uri_auth+alice_the_artist_profile_token+'/').content.decode('utf-8'))['auth']
	

	def test_get_no_suggestion(self):
		# Verifies empty suggestions
		client = Client()
		bob_the_socialaware_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_socialaware_twin_profile.token+'/', 
			content_type='application/json', data=page_one(self.bob_the_socialaware_twin_auth))
		contx = json.loads(bob_the_socialaware_twin_page1_suggestion.content.decode('utf-8'))['recommendation']
		self.assertEqual(contx, 'No known objects')

	def test_get_suggestion(self):
		# Get a valid suggestions by interacting with two profiles
		client = Client()
		client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/', 
			content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))

		bob_the_artist_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_artist_twin_profile.token+'/', 
			content_type='application/json', data=page_one(self.bob_the_artist_twin_auth))
		contx = json.loads(bob_the_artist_twin_page1_suggestion.content.decode('utf-8'))['recommendation']
		# First element of the given list
		self.assertEqual(contx, '[0]')

	def test_profile_browsing_error(self):
		# Checks for the 5 second browsing rule
		# Attempts to fails
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

	def test_get_suggestion_compare_interest_suggestion(self):
		"""
			Testing with the most interests in common despite all the other common factors
		"""
		# Client type Request
		client = Client()
		# Bob the social aware has no interests in common with Bob the artist
		# Bob the social aware selects a selectable item from page 1
		client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))
		# Alice has a lot in common with bob the artist, but has a different gender.
		# Alice selects another object
		client.post(self.uri_add_selectable+self.alice_the_artist_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.alice_the_artist_auth, 1))

		bob_the_artist_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_artist_twin_profile.token+'/', 
		 content_type='application/json', data=page_one(self.bob_the_artist_twin_auth))

		contx = json.loads(bob_the_artist_twin_page1_suggestion.content.decode('utf-8'))['recommendation']
		# First element of the given list
		self.assertEqual(contx, '[1, 0]')

	def test_neural_network_learning(self):
		"""
			Tests the learning of a profile
		"""
		client = Client()
		# Bob the social aware has no interests in common with Bob the artist
		# Bob the social aware selects a selectable item from page 1
		client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))
		# Alice has a lot in common with bob the artist, but has a different gender.
		# Alice selects another object
		client.post(self.uri_add_selectable+self.alice_the_artist_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.alice_the_artist_auth, 1))

		bob_the_artist_twin_page1_suggestion = client.post(self.uri_suggestion+self.bob_the_artist_twin_profile.token+'/', 
		 content_type='application/json', data=page_one(self.bob_the_artist_twin_auth))

		client.post(self.uri_add_selectable+self.bob_the_artist_twin_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.bob_the_artist_twin_auth, 0))

		# The profile before running the algorith did not have an Interest for Travel
		self.assertTrue(0.0 < ProfileInterest.objects.get(profile=self.bob_the_artist_twin_profile, interest__name="Travel").level < 0.15)
		# His interest for Craft is re-evaluated
		self.assertTrue(1.0 > ProfileInterest.objects.get(profile=self.bob_the_artist_twin_profile, interest__name="Craft").level > 0.90)
	
	def test_neo4j_connected(self):
		"""
			Allows us to verify the connection with neo4j server
		"""
		client = Client()
		response = client.post(self.uri_add_selectable+self.bob_the_socialaware_twin_profile.token+'/',
		 content_type='application/json', data=page_one_objects(self.bob_the_socialaware_twin_auth, 0))
		status = json.loads(response.content.decode('utf-8'))['inter']
		self.assertNotEqual(status,'e_neo4j_Disconnected')
	
	def test_uu_test(self):
		"""
		Assert a change after selecting a profile that has an object in common from another website
		"""
		base = "http://localhost:8000"
		# Pro1 and Pro1a have no interests in common, Pro1 and Pro2 have two interests in common
		pro1 = requests.post(base+self.uri_creation, data=made_up_profiles(1), headers={'Content-Type': 'application/json'})
		pro1a = requests.post(base+self.uri_creation, data=made_up_profiles(0), headers={'Content-Type': 'application/json'})
		pro2= requests.post(base+self.uri_creation, data=made_up_profiles(2), headers={'Content-Type': 'application/json'})

		pro1_token = json.loads(pro1.content.decode('utf-8'))['profile']
		pro1a_token = json.loads(pro1a.content.decode('utf-8'))['profile']
		pro2_token = json.loads(pro2.content.decode('utf-8'))['profile']

		pro1_auth = json.loads(requests.get(base+self.uri_auth+pro1_token+'/').content.decode('utf-8'))['auth']
		pro1a_auth = json.loads(requests.get(base+self.uri_auth+pro1a_token+'/').content.decode('utf-8'))['auth']
		pro2_auth = json.loads(requests.get(base+self.uri_auth+pro2_token+'/').content.decode('utf-8'))['auth']

		requests.post(base+self.uri_add_selectable+pro1_token+'/', data=page_two_objects(pro1_auth, 5), headers={'Content-Type': 'application/json'})
		requests.post(base+self.uri_add_selectable+pro1a_token+'/', data=page_one_objects(pro1a_auth, 0), headers={'Content-Type': 'application/json'})
		requests.post(base+self.uri_add_selectable+pro2_token+'/', data=page_one_objects(pro2_auth, 1), headers={'Content-Type': 'application/json'})
		suggestion_r = requests.post(base+self.uri_suggestion+pro1_token+'/', data=page_one(pro1_auth), headers={'Content-Type': 'application/json'})
		contx_a = ast.literal_eval(json.loads(suggestion_r.content.decode('utf-8'))['base'])[0]
		contx_b = ast.literal_eval(json.loads(suggestion_r.content.decode('utf-8'))['base'])[1]
		contx_flag = json.loads(suggestion_r.content.decode('utf-8'))['state']
		requests.post(base+self.uri_add_selectable+pro1a_token+'/', data=page_two_objects(pro1a_auth, 3), headers={'Content-Type': 'application/json'})
		suggestion2_r = requests.post(base+self.uri_suggestion+pro1_token+'/', data=page_one(pro1_auth), headers={'Content-Type': 'application/json'})
		contx2_a = ast.literal_eval(json.loads(suggestion2_r.content.decode('utf-8'))['base'])[0]
		contx2_b = ast.literal_eval(json.loads(suggestion2_r.content.decode('utf-8'))['base'])[1]
		self.assertTrue(contx2_a < contx_a)
		self.assertTrue(contx2_b > contx_b)
		#  Element at index zero must become lower as it has a website in common with profile 1a
		#  Element at index one must become higher as it has a no website in common with profile 2

