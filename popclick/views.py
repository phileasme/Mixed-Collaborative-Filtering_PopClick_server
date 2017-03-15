from __future__ import division
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
import random as rand
from django.core import serializers
from datetime import datetime
from django.utils import timezone
import requests
import json
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.db import IntegrityError
from .models import Interest, Visit, Website, SecureAuth, Page, Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
        RelationshipTo, RelationshipFrom)
from .models import PageN, WebsiteN, ProfileN
from popclick.populate_suggestable import *
from django.db.models import Max, Min
from numpy import *
from operator import itemgetter
import numpy as np
from neomodel import db as neodb
# from py2neo import cypher
from sklearn.preprocessing import normalize
from neomodel import config as neoconfig
def index(request):
    return HttpResponse("Glad to check that the PopClick server is online.")

@csrf_exempt
def viewkey(request, key):
    own_profile = Profile.objects.get(token=key)
    own_key = SecureAuth.objects.get(profile=own_profile)
    if own_key:
        context = {'recommendation': "Alive"+own_key.key}
    else:
        context = {'recommendation': "Dead"}
    return render(request, 'viewkey.json', context)

@csrf_exempt
def keygen(request, key):
    own_profile = Profile.objects.get(token=key)
    own_key = SecureAuth(profile=own_profile, key=own_profile.auth)
    own_key.save()
    return HttpResponse("New Key generated")

# def remove_mistake(request, ):
    # Already visited in the last 5 seconds

# Profile Based Collaborative filtering
@csrf_exempt
def get_suggestion(request, token):
    if request.method == 'POST':
        # Loading Received information to a json format
        received_json_data = json.loads(request.body.decode('utf-8'))
        object_auth = received_json_data['profile']
        #  Getting profile information
        own_profile = Profile.objects.get(token=token)
        own_key = SecureAuth.objects.get(profile=own_profile).key
        # Making sure the profile is activated and in order
        if own_profile and own_profile.activated and own_key == str(object_auth):
            # Check if the page was already visited by the suse in last 5 seconds
            Visit.objects.filter(profile=own_profile).order_by('-id')[1]
            # Get last visit of user
            # Get last selected element of user lochref href

            pageobjects = received_json_data['pageobjects']
            try:
                # Getting web page origin
                base_uri = pageobjects[0][0]
                handle_visit(own_profile, base_uri)
                # Extracting the received pageobjects
                received_pageobjects_hrefs = [o[1] for o in pageobjects]
                received_pageobjects_text = [o[2] for o in pageobjects]
                received_pageobjects_selectors = [o[3] for o in pageobjects]
            # Throw an Index Error if there is a missmatch.
            except IndexError:
                context = {'base': "Current", 'recommendation': "None"}
                return render(request, 'suggestions.json', context)
            try:
                # Cross reference objects visible to the user and the objects stored
                page = Page.objects.get(href=base_uri)
                pageobjects = PageObject.objects.filter(page=page)
                match_pageobjects = set(pageobjects)
                matching_pageobjects_set = set(pageobjects.filter(text__in=received_pageobjects_text).values_list('id', flat=True))
                matching_pageobjects_set.update(pageobjects.filter(href__in=received_pageobjects_hrefs).values_list('id', flat=True))
                matching_pageobjects = pageobjects.filter(pk__in=matching_pageobjects_set)
                profiles_pageobjects = ProfilePageobject.objects.filter(pageobject__in=matching_pageobjects)
                profiles = Profile.objects.filter(id__in=profiles_pageobjects.values('profile').distinct())
                profiles_interests = ProfileInterest.objects.filter(profile__in=profiles)
                selectable_values = []
                # Normalized profile pageobject selection among profiles po.
                # Dictionaries for the profile page selections, profile ages, Standardized profile interests, standardized genders
                nm_pg_select = {}
                nm_pr_ages = {}
                std_pr_int = {}
                std_gender = {}
                # Find the oldest and youngest individuals
                lowest_age = profiles.aggregate(Min('age'))['age__min']
                highest_age = profiles.aggregate(Max('age'))['age__max']
                # List of all the interests
                interests = [i.name for i in Interest.objects.all().order_by('name')]
                # If their are no records of ages
                if highest_age is None or lowest_age is None:
                    context = {'base': base_uri, 'obj': "No known objects"}
                    return render(request, 'suggestions.json', context)
                # If the database only hase one user we have to handle a small age difference.
                if highest_age - lowest_age == 0:
                    lowest_age = 2014
                # The different types of genders
                genders = ['Female', 'Male', 'Other', 'Irrelevant']

                # Standardising profile based attributes : Gender, Interests | Normalising profile based attributes : Age, Selections
                for profile in profiles :
                    # Retrieving highest and lowest number of selections.
                    lowest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Min('selections'))['selections__min']
                    highest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Max('selections'))['selections__max']
                    if int(highest_nb_selections) - int(lowest_nb_selections) == 0:
                        highest_nb_selections = highest_nb_selections + 1

                    # Normalising selectable value per pageobject
                    for pr_po in profiles_pageobjects.filter(profile=profile):
                        nm_pg_select[str(pr_po.id)] = float(pr_po.selections-int(lowest_nb_selections))/float(int(highest_nb_selections)-int(lowest_nb_selections))

                    nm_pr_ages[str(profile.id)] = float((profile.age-lowest_age)/(highest_age-lowest_age))
                    # Retreiving the profile's interests
                    pr_int = [pi['interest'] for pi in profiles_interests.filter(profile=profile).values('interest')]
                    # Index matching the interest location within the list of all known interests(alphabetically)
                    pr_int_index = [interests.index(pri) for pri in pr_int]

                    # Array of zero's for a standardized
                    standardized_profile_interests = [0]*(len(interests))
                    standardized_profile_gender = [0]*(len(genders))
                    # Standardising the profile interests and gender creating two rows containing 0's and 1's
                    for it in pr_int_index:
                        standardized_profile_interests[it] = 1
                    standardized_profile_gender[genders.index(profile.gender)] = 1

                    # Add standardised list of profile interests to the dictionary of standardised interests
                    std_pr_int[str(profile.id)] = standardized_profile_interests
                    # Add standardised list of profile gender to the dictionary of standardised gender 
                    std_gender[str(profile.id)] = [standardized_profile_gender]
                
                # Ordered list of pageobjects
                po_indexs = []
                # Dictionary of normalised Age per profile per page object
                po_norm_age = {}
                #  Dictionary of normalised Selections per profile per page objects
                po_norm_select = {}
                # For each object obtain add each user profile interests or gender value
                # (The matrix will be normalized)
                po_std_norm_interests_matrix = []
                po_std_norm_gender_matrix = []
                for po in matching_pageobjects.order_by('href'):
                    # Adding page object to the list to allow indexing
                    po_indexs.append(po)
                    # Number of profiles who used the page object
                    po_l = int(profiles_pageobjects.filter(pageobject=po).distinct().count())
                    # Default values
                    pr_po_mn_select = 0
                    pr_po_mn_age = 0
                    pr_po_std_mn_interests = []
                    pr_po_std_mn_gender = []
                    # For each profile mapped to an object
                    for pro in profiles_pageobjects.filter(pageobject=po):
                        # Add the profile normalised selections and age of the object/Profile
                        pr_po_mn_select += float(nm_pg_select[str(pro.id)])
                        pr_po_mn_age += float(nm_pr_ages[str(pro.profile.id)])
                        # Add to the array interest/gender array or initialise it
                        if len(pr_po_std_mn_interests) == 0:
                            pr_po_std_mn_interests = std_pr_int[str(pro.profile.id)]
                        else:
                            pr_po_std_mn_interests = np.add(pr_po_std_mn_interests, std_pr_int[str(pro.profile.id)])
                        if len(pr_po_std_mn_gender) == 0:
                            pr_po_std_mn_gender = std_gender[str(pro.profile.id)]
                        else:
                            pr_po_std_mn_gender = np.add(pr_po_std_mn_gender, std_gender[str(pro.profile.id)])
                    # Page object standardised to be normalised interest/gender matrix
                    po_std_norm_interests_matrix[len(po_std_norm_interests_matrix):] = [pr_po_std_mn_interests]
                    po_std_norm_gender_matrix[len(po_std_norm_gender_matrix):] = pr_po_std_mn_gender
                    # Normalise the selection and age prior
                    pr_po_mn_select /= po_l
                    po_norm_select[po] = [pr_po_mn_select]
                    pr_po_mn_age /= po_l
                    po_norm_age[po] = [pr_po_mn_age]

                complete_matrix = []
                # Convert to numpy array
                postdnormintmtx = np.array(po_std_norm_interests_matrix)
                postdnormgendmtx = np.array(po_std_norm_gender_matrix)
                np.seterr(divide='ignore', invalid='ignore')

                # Create the complete matrix
                # Matrix structure : age, interests , gender, selection
                for po in matching_pageobjects.order_by('href'):
                    complete_matrix.append(np.append(np.append(np.append(po_norm_age[po],postdnormintmtx[po_indexs.index(po)]),postdnormgendmtx[po_indexs.index(po)]),po_norm_select[po]))
                
                # Individual Row, Could be simplified to simply getting the actual user row in the matrix
                standardized_own_profile_gender = [0]*(len(genders))
                standardized_own_profile_interests = [0]*(len(interests))
                standardized_own_profile_gender[genders.index(own_profile.gender)] = 1
                prof_int = [pi['interest'] for pi in profiles_interests.filter(profile=own_profile).values('interest')]
                prof_int_index = [interests.index(pri) for pri in prof_int]
                for it in prof_int_index:
                    standardized_own_profile_interests[it] = 1
                own_porfile_properties = (np.append([float((profile.age-lowest_age)/(highest_age-lowest_age))], np.append(standardized_own_profile_interests, np.append(standardized_own_profile_gender,[1.0]))))  
                
                # Normalize columns
                complete_matrix = np.matrix(normalize(complete_matrix, axis=0, norm='l1'))
                # Euclidean distance calculation
                profile_po_distance = []
                for rows in range(complete_matrix.shape[0]):
                    current_row = 0
                    for columns in range(complete_matrix.shape[1]):
                        current_row += np.square(own_porfile_properties[columns]-complete_matrix.item(rows,columns))
                    profile_po_distance.append((po_indexs[rows],(np.sqrt(current_row))))
                # Sorted list of distances
                profile_po_distance = sorted(profile_po_distance, key=itemgetter(1))
                pro_po_d = []
                pro_po_t = []
                pro_po_h = []
                for item in profile_po_distance:
                    if item[0].text in received_pageobjects_text:
                        # pro_po_t.append(item[0].text)
                        # pro_po_d.append(0)
                        pro_po_d.append(received_pageobjects_text.index(item[0].text))
                    else:
                        # pro_po_d.append(1)
                        # pro_po_h.append(item[0].href)
                        pro_po_d.append(received_pageobjects_hrefs.index(item[0].href))

                # # Gives the index of the element Matching its rank
                sent_recommendation = []
                for i in pro_po_d:
                    if i not in sent_recommendation:
                        sent_recommendation.append(i)
                # obbb = len(ProfileN.nodes.get(token=token).get_tokens_from_common_Websites())

                # Just to print
                context = {'base': ProfileN.nodes.get(token=token).get_tokens_from_common_Websites(page=base_uri), 'recommendation_text': json.dumps(pro_po_t), 'recommendation_href':json.dumps(pro_po_h), 'recommendation':pro_po_d}

            except (Page.DoesNotExist):
                context = {'base': base_uri, 'recommendation': "No known objects"}
            except KeyError as e:
                context = {'base': base_uri, 'recommendation': "Cross matching issue"}
            return render(request, 'suggestions.json', context)
# def KNN_regression()

# def getTrend()
# def user_user_recommendation:
    

@csrf_exempt
# Href unique constraint violation
def populate_selectable(request, token):
    if request.method == 'POST':
        received_json_data = json.loads(request.body.decode('utf-8'))
        object_profile = received_json_data['profile']
        object_pageobject = received_json_data['pageobject']
        object_interaction = received_json_data['interaction']
        object_auth = object_profile[0]
        object_logtime = datetime.strptime(object_profile[1], r'%Y-%m-%d %H:%M')
        profile = Profile.objects.get(token=token)
        if profile and profile.activated and SecureAuth.objects.get(profile=profile).key == str(object_auth):
            object_website = object_pageobject[4]
            object_page_path = object_pageobject[5]
            object_page = object_pageobject[0]#check for valid url
            object_href = object_pageobject[1]
            object_text = object_pageobject[2]
            object_selector = object_pageobject[3]
            object_operation =  object_interaction[0]
            object_clicks = object_interaction[1]
            if "localhost:" not in object_page:
                handle_Website(object_website)
                page = handle_Page(object_website, object_page_path, object_page)
                pageobject = handle_PageObject(object_selector, object_href, object_page, object_text)
                handle_visit(profile, page)
                profile_pageobject = handle_Profile_PageObject(profile, pageobject)
                handle_PageobjectLog(profile, pageobject)
                with neodb.transaction:
                    websiten = WebsiteN.get_or_create({'host': ''+object_website})
                    pagen = PageN.get_or_create({'href': object_href})
                    websiten = WebsiteN.nodes.get(host=object_website)
                    pagen = PageN.nodes.get(href=object_href)
                    pagen.website.connect(websiten)
                    profilen = ProfileN.get_or_create({'token': ''+profile.token})
                    profilen = ProfileN.nodes.get(token=token)
                    profilen.page.connect(pagen)
                    profilen.website.connect(websiten)
                context = { 'prof':object_profile, 'obj':object_pageobject, 'inter':object_interaction}
            else:
                context = { 'storing': 'not'}
        else:
            context = { 'error' : 'not_activated'}
        return render(request, 'selectable_addition.json', context)


@csrf_exempt
def get_initial_auth(request, token):
    if request.method == 'GET':
        profile = Profile.objects.get(token=token)
        secure_auth = SecureAuth.objects.get(profile=profile).key
        if profile.activated == False:
            context = { 'auth' : secure_auth }
            profile.activated = True
            profile.save()
            with neodb.transaction:
                profilen = ProfileN.get_or_create({'token': ''+profile.token})
        else:
            context = { 'auth' : '' }
        return render(request, 'auth.json', context)

@csrf_exempt
def create_profile(request):
    Interests = ['News & Media','Fashion','Tech','Finance & Economics','Music','Cars','Sports','Games & Tech','Shopping','Literature','Travel','Arts','Social Awareness','Science','Movies & Theatre','Craft']
    if request.method == 'POST':
        # JSON decode error handling
        received_json_data= json.loads(request.body.decode('utf-8'))
        if profile_create_check(received_json_data, Interests) == "VALIDATED":
            #Have to add a response if one of age, token, auth, gender, logtime is wrong
            private_k = randToken()
            new_profile = Profile(
                    age=int(datetime.today().year)-int(received_json_data['age']), 
                    token=randToken(),
                    gender=received_json_data['gender'],
                    logtime=datetime.strptime(received_json_data['logtime'], r'%Y-%m-%d %H:%M'))
            new_profile.save()
            new_secureauth = SecureAuth(profile=new_profile, key=private_k)
            new_secureauth.save()
            for interest in received_json_data['interests']:
                if interest in Interests:
                    new_interest = Interest(name=interest)
                    new_interest.save()
                    new_profile_interest = ProfileInterest(profile=new_profile, interest=new_interest)
                    new_profile_interest.save()
                #  Convert to json array : data['interests']
            context = { 'profile' : new_profile }
        else:
            context = { 'profile_error' : profile_create_check(received_json_data, Interests) }
        return render(request, 'create_profile.json', context)

# A profile must have a valid age, gender, logtime and at least 3 interests.
def profile_create_check(json_object, Interests):
    if {"age", "gender", "logtime", "interests"} <= json_object.keys():
        if not(RepresentsInt(json_object['age']) and int(json_object['age']) > 3 and int(json_object['age']) < 120):
            return "INVALID_AGE"
        else:
            if not str(json_object['gender']) in ["Male","Female","Other","Irrelevant"]:
                return "INVALID_GENDER"
            else:
                # if datetime.strptime(received_json_data['logtime'], r'%Y-%m-%d %H:%M')
                try:
                    d = datetime.strptime(json_object['logtime'], r'%Y-%m-%d %H:%M')
                    own_interests = 0
                    for inter in json_object['interests']:
                        if inter in Interests:
                            own_interests+=1
                    if not 3 <= own_interests < len(Interests):
                        return own_interests
                    else:
                        return "VALIDATED"
                except ValueError:
                    return "WRONG_DATE_FORMAT"
    else:
        return "MISSING_ATTRIBUTE"

# If the element can be represented as an integer
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def profiles(request):
    profiles = Profile.objects.all()
    interests = Interest.objects.all()
    profile_interests = {}
    for each_prof in profiles:
        # Getting the interest of the profile
        curr_interests = each_prof.interests.all()
        # Create empty array
        curr_int_names = []
        # Iterate through the interests of the profile
        for each_int in curr_interests:
            # Append the to list of names
            curr_int_names.append(each_int.name)
        profile_interests[each_prof.token] = curr_int_names
    context = { 'profile_interests': profile_interests, 'profiles': profiles, 'interests': interests}
    return render(request, 'profiles.html', context)

def randToken():
    a = '0123456789abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ'
    return "".join([rand.choice(a) for _ in range(20)])