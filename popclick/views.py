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

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def handle_Website(host):
    website, created = Website.objects.get_or_create(host=host)
    return website

def handle_Page(host, path, href):
    website, created = Website.objects.get_or_create(host=host)
    page = Page.objects.get_or_create(path=path, href=href, website=website)
    return page

def handle_PageObject(selector, href, page, text):
    page = Page.objects.get(href=page)
    pageobject, created = PageObject.objects.get_or_create(selector=selector, href=href, page=page)
    pageobject.text = text
    pageobject.selections += 1 
    pageobject.save()
    return pageobject

def handle_Profile_PageObject(profile, pageobject):
    new_profile_pageobject, created = ProfilePageobject.objects.get_or_create(profile=profile, pageobject=pageobject)
    new_profile_pageobject.selections += 1
    new_profile_pageobject.save()
    return new_profile_pageobject

def handle_Profile_PageobjectLog(profile_pageobject, logtime):
    profile_pageobject_log = ProfilePageobjectLog(profile_pageobject=profile_pageobject, logtime=logtime)
    profile_pageobject_log.save()

def handle_visit(profile, page):
    page = Page.objects.get(href=page)
    visit, created = Visit.objects.get_or_create(profile=profile, page=page)
    visit.counter += 1
    visit.save()
    return visit

@csrf_exempt
# def suggest_main(request, token):
    

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