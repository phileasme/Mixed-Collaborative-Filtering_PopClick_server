from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
import random
from django.core import serializers
from datetime import datetime
from django.utils import timezone
import requests
import json
from django.http import StreamingHttpResponse
from .models import Interest, Visit, Website, Page, Profile, ProfileInterest, PageObject, PageInterest, PageobjectInterest, ProfilePageobject, ProfilePageobjectLog 
from popclick.populate_suggestable import *
from django.db.models import Max
from numpy import *
import numpy as np
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def get_suggestion(request, token):
    if request.method == 'POST':
        received_json_data = json.loads(request.body.decode('utf-8'))

        object_auth = received_json_data['profile']
        # Array of page objects
        profile = Profile.objects.get(token=token, auth=object_auth)
        if profile and profile.activated:
            pageobjects = received_json_data['pageobjects']
            base_uri = pageobjects[0][0]
            received_pageobjects_hrefs = [o[1] for o in pageobjects]
            received_pageobjects_text = [o[2] for o in pageobjects]
            received_pageobjects_selectors = [o[3] for o in pageobjects]
            try:
                page = Page.objects.get(href=base_uri)
                matching_pageobjects = PageObject.objects.filter(page=page).filter(href__in=received_pageobjects_hrefs)
                profiles_pageobjects = ProfilePageobject.objects.filter(pageobject__in=matching_pageobjects)
                profiles = Profile.objects.filter(id__in=profiles_pageobjects.values('profile').distinct())
                profiles_interests = ProfileInterest.objects.filter(profile__in=profiles)
                # Normalized profile pageobject selection among profiles po.
                nm_pg_select = {}
                nm_pr_ages = {}
                std_pr_int = {}
                highest_age = profiles.aggregate(Max('age'))['age__max']
                interests = []
                for i in Interest.objects.all().order_by('name'):
                    interests[len(interests):] = i.name
                for profile in profiles :
                    highest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Max('selections'))['selections__max']
                    for pr_po in profiles_pageobjects.filter(profile=profile):
                        nm_pg_select[str(pr_po.id)] = (pr_po.selections/int(highest_nb_selections))
                    nm_pr_ages[str(profile.id)] = (profile.age/int(highest_age))
                    pr_int_index = []
                    pr_int = []
                    for pi in profiles_interests.filter(profile=profile).values('interest'):
                        for index, pi['interest'] in enumerate(Interest.objects.all().order_by('name')):
                            pr_int_index[len(pr_int_index):] = index
                    # Fill list with zero execpt at certain indices
                






                # indices = [i for i, s in enumerate(interests) if  in s]
                #1 Prepare clicks -> Take clicks of each object / clicks of the object with highest amount
                #2 Prepare interests -> Take all the existing interests | Place a 1 if that is one of the interests
                #2 Array of interests, instanciate that list replace with zero if not in users interest else 1
                #1 One simple column
                #3 Gender similar to interests


                # .values_list('profile', flat=True).distinct()
                context = {'base': base_uri, 'obj': pr_int[0]['interest'] }
            except Page.DoesNotExist:
                context = {'base': base_uri, 'obj': "No known objects"}

            return render(request, 'suggestions.json', context)

@csrf_exempt
def populate_selectable(request, token):
    if request.method == 'POST':
        received_json_data = json.loads(request.body.decode('utf-8'))

        object_profile = received_json_data['profile']
        object_pageobject = received_json_data['pageobject']
        object_interaction = received_json_data['interaction']
        object_auth = object_profile[0]
        object_logtime = datetime.strptime(object_profile[1], r'%Y-%m-%d %H:%M')
        profile = Profile.objects.get(token=token, auth=object_auth)
        if profile and profile.activated:
            object_website = object_pageobject[4]
            object_page_path = object_pageobject[5]
            object_page = object_pageobject[0]#check for valid url
            object_href = object_pageobject[1]
            object_text = object_pageobject[2]
            object_selector = object_pageobject[3]
            object_operation =  object_interaction[0]
            object_clicks = object_interaction[1]
            handle_Website(object_website)
            page = handle_Page(object_website, object_page_path, object_page)
            pageobject = handle_PageObject(object_selector, object_href, object_page, object_text)
            profile_pageobject = handle_Profile_PageObject(profile, pageobject)
            handle_Profile_PageobjectLog(profile_pageobject, object_logtime)
            handle_visit(profile, object_page)
            context = { 'prof':object_profile, 'obj':object_pageobject, 'inter':object_interaction}
        else:
            context = { 'error' : 'not_activated'}
        return render(request, 'selectable_addition.json', context)


@csrf_exempt
def get_initial_auth(request, token):
    if request.method == 'GET':
        profile = Profile.objects.get(token=token)
        if profile.activated == False:
            context = { 'auth' : profile.auth }
            profile.activated = True
            profile.save()
        else:
            context = { 'auth' : '' }
        return render(request, 'auth.json', context)

@csrf_exempt
def create_profile(request):
    if request.method == 'POST':
        received_json_data= json.loads(request.body.decode('utf-8'))
        if 'age' in received_json_data:
            #Have to add a response if one of age, token, auth, gender, logtime is wrong
            new_profile = Profile(
                    age=received_json_data['age'], 
                    token=randToken(),
                    auth=randToken(),
                    gender=received_json_data['gender'],
                    logtime=datetime.strptime(received_json_data['logtime'], r'%Y-%m-%d %H:%M'))
            new_profile.save()
            for interest in received_json_data['interests']:
                new_interest = Interest(name=interest)
                new_interest.save()
                new_profile_interest = ProfileInterest(profile=new_profile, interest=new_interest)
                new_profile_interest.save()
                #  Convert to json array : data['interests']
            context = { 'profile' : new_profile }
            return render(request, 'create_profile.json', context)
            
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
    return "".join([random.choice(a) for _ in range(20)])