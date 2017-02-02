from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
import random
from django.core import serializers
from datetime import datetime
import requests
import json
from django.http import StreamingHttpResponse
from .models import Profile, Interest, ProfileInterest

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def create_profile(request):
    if request.method == 'POST':
        # data = request.POST
        received_json_data= json.loads( request.body.decode('utf-8') )
        if 'age' in received_json_data:
            new_profile = Profile(
                    age=received_json_data['age'], 
                    token=randToken(),
                    auth=randToken(),
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