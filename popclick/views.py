from __future__ import division
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
import random
from django.core import serializers
from datetime import datetime
from django.utils import timezone
import requests
import json
from django.db.models import Q
from django.http import StreamingHttpResponse
from .models import Interest, Visit, Website, Page, Profile, ProfileInterest, PageObject, PageInterest, PageobjectInterest, ProfilePageobject, ProfilePageobjectLog 
from popclick.populate_suggestable import *
from django.db.models import Max, Min
from numpy import *
from operator import itemgetter
import numpy as np
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def get_suggestion(request, token):
    if request.method == 'POST':
        received_json_data = json.loads(request.body.decode('utf-8'))

        object_auth = received_json_data['profile']
        # Array of page objects
        own_profile = Profile.objects.get(token=token, auth=object_auth)
        if own_profile and own_profile.activated:
            pageobjects = received_json_data['pageobjects']
            base_uri = pageobjects[0][0]
            received_pageobjects_hrefs = [o[1] for o in pageobjects]
            received_pageobjects_text = [o[2] for o in pageobjects]
            received_pageobjects_selectors = [o[3] for o in pageobjects]
            # Analyze if selector is necessary : If url has a Hash character then it is
            # See if the text is meaningful : If there is Only one element with a text for a text then it is
            # Bug Fix : We don't get all the elements
            # Match href / href & text / text & selector
            # QuerySets are bad at handling when we have many.
            # Limit the number of posted queries?
            try:
                page = Page.objects.get(href=base_uri)
                pageobjects = PageObject.objects.filter(page=page)
                match_pageobjects = set(pageobjects)
                matching_pageobjects = pageobjects.filter(href__in=received_pageobjects_hrefs)
                matching_pageobjects_set = set(pageobjects.filter(href__in=received_pageobjects_hrefs))
                # for index, mpb in enumerate(pageobjects):
                #     try:
                #         matching_pageobjects_set.add(pageobjects.get(text=received_pageobjects_text[index]))
                #     except PageObject.DoesNotExist:
                #         matching_pageobjects_set = matching_pageobjects_set

                profiles_pageobjects = ProfilePageobject.objects.filter(pageobject__in=matching_pageobjects)
                profiles = Profile.objects.filter(id__in=profiles_pageobjects.values('profile').distinct())
                profiles_interests = ProfileInterest.objects.filter(profile__in=profiles)

                # Normalized profile pageobject selection among profiles po.
                nm_pg_select = {}
                nm_pr_ages = {}
                std_pr_int = {}
                std_gender = {}
                lowest_age = profiles.aggregate(Min('age'))['age__min']
                highest_age = profiles.aggregate(Max('age'))['age__max']
                interests = [i.name for i in Interest.objects.all().order_by('name')]
                if highest_age - lowest_age == 0:
                    lowest_age = 0
                genders = ['Female', 'Male', 'Other', 'Irrelevant']
                for profile in profiles :
                    lowest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Min('selections'))['selections__min']
                    highest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Max('selections'))['selections__max']
                    if highest_nb_selections - lowest_nb_selections == 0:
                        lowest_nb_selections = 0
                    for pr_po in profiles_pageobjects.filter(profile=profile):
                        nm_pg_select[str(pr_po.id)] = (pr_po.selections-int(lowest_nb_selections))/(int(highest_nb_selections)-int(lowest_nb_selections))
                    nm_pr_ages[str(profile.id)] = (profile.age-int(lowest_age))/(int(highest_age)-int(lowest_age))
                    
                    pr_int = [pi['interest'] for pi in profiles_interests.filter(profile=profile).values('interest')]
                    pr_int_index = [interests.index(pri) for pri in pr_int]
                    standardized_profile_interests = [0]*(len(interests))
                    for it in pr_int_index:
                        standardized_profile_interests[it] = 1
                    std_pr_int[str(profile.id)] = standardized_profile_interests
                    standardized_profile_gender = [0]*(len(genders))
                    standardized_profile_gender[genders.index(profile.gender)] = 1
                    std_gender[str(profile.id)] = [standardized_profile_gender]
                po_indexs = []
                # po_std_norm_interests = {}
                po_norm_age = {}
                # po_std_norm_gender = {}
                po_norm_select = {}

                # For each object obtain the average of each user profile choice
                po_std_norm_interests_matrix = []
                po_std_norm_gender_matrix = []
                sss = matching_pageobjects.order_by('href').count()
                ssd = [str(o.text) for o in matching_pageobjects.order_by('href')]
                ordered_pageobjects = matching_pageobjects.order_by('href')
                for po in matching_pageobjects.order_by('href'):
                    po_indexs.append(po)
                    po_l = int(profiles_pageobjects.filter(pageobject=po).count())
                    pr_po_mn_select = 0
                    pr_po_mn_age = 0
                    pr_po_std_mn_interests = []
                    pr_po_std_mn_gender = []
                    for pro in profiles_pageobjects.filter(pageobject=po).order_by('pageobject'):
                        pr_po_mn_select += float(nm_pg_select[str(pro.id)])
                        pr_po_mn_age += float(nm_pr_ages[str(pro.profile.id)])
                        if len(pr_po_std_mn_interests) == 0:
                            pr_po_std_mn_interests = std_pr_int[str(pro.profile.id)]
                        else:
                            pr_po_std_mn_interests = np.add(pr_po_std_mn_interests, std_pr_int[str(pro.profile.id)])
                        if len(pr_po_std_mn_gender) == 0:
                            pr_po_std_mn_gender = std_gender[str(pro.profile.id)]
                        else:
                            pr_po_std_mn_gender = np.add(pr_po_std_mn_gender, std_gender[str(pro.profile.id)])
                    po_std_norm_interests_matrix[len(po_std_norm_interests_matrix):] = [pr_po_std_mn_interests]
                    po_std_norm_gender_matrix[len(po_std_norm_gender_matrix):] = pr_po_std_mn_gender
                    # Still have to transform this to a proper matrix
                    pr_po_mn_select /= po_l
                    po_norm_select[po] = [pr_po_mn_select]
                    pr_po_mn_age /= po_l
                    po_norm_age[po] = [pr_po_mn_age]

                complete_matrix = []
                #  --- Next step
                #  ----First : You concatenate lists (rows)
                #  --- Second : You merge matrices 
                #  Apply KNN comparing user profile. <-- Simple KNN not considering past user exterior page experience
                postdnormintmtx = np.array(po_std_norm_interests_matrix)
                postdnormgendmtx = np.array(po_std_norm_gender_matrix)
                np.seterr(divide='ignore', invalid='ignore')
                for po in matching_pageobjects.order_by('href'):
                    complete_matrix.append(np.append(np.append(np.append(po_norm_age[po],postdnormintmtx[po_indexs.index(po)]),postdnormgendmtx[po_indexs.index(po)]),po_norm_select[po]))
                # Euclidean distance calculation
                # Matrix structure : age, interests , gender, selection
                standardized_own_profile_gender = [0]*(len(genders))
                standardized_own_profile_gender[genders.index(own_profile.gender)] = 1
                prof_int = [pi['interest'] for pi in profiles_interests.filter(profile=own_profile).values('interest')]
                prof_int_index = [interests.index(pri) for pri in prof_int]
                standardized_own_profile_interests = [0]*(len(interests))
                for it in prof_int_index:
                    standardized_own_profile_interests[it] = 1
                complete_matrix_averages = np.mean(complete_matrix, axis=0)
                if len(po_std_norm_interests_matrix) != 0 and len(postdnormintmtx) != 0:
                    po_std_norm_interests_matrix = np.nan_to_num((postdnormintmtx-postdnormintmtx.min(axis=0)) / (postdnormintmtx.max(axis=0)-postdnormintmtx.min(axis=0)))

                if len(po_std_norm_gender_matrix) != 0 and len(postdnormgendmtx) != 0:
                    po_std_norm_gender_matrix = np.nan_to_num((postdnormgendmtx-postdnormgendmtx.min(axis=0)) / (postdnormgendmtx.max(axis=0)-postdnormgendmtx.min(axis=0)))

                own_porfile_properties = (np.append([(float((float(own_profile.age)-lowest_age)/(highest_age-lowest_age)))], np.append(standardized_own_profile_interests, np.append(standardized_own_profile_gender,[1.0]))))  
                complete_matrix = np.matrix(complete_matrix)
                profile_po_distance = []
                for rows in range(complete_matrix.shape[0]):
                    current_row = 0
                    for columns in range(complete_matrix.shape[1]):
                        current_row += np.square(own_porfile_properties[columns]-complete_matrix.item(rows,columns))
                    profile_po_distance.append((po_indexs[rows],(np.sqrt(current_row))))
                profile_po_distance = sorted(profile_po_distance, key=itemgetter(1))
                pro_po_d = []
                for item in profile_po_distance:
                    pro_po_d.append(received_pageobjects_hrefs.index(item[0].href))
                # profile_match_distance = po_indexs

                # # Gives the index of the element Matching its rank
                # for ind, ele in profile_po_distance:
                #     profile_match_distance[profile_po_distance_order.index(ele)] = po_indexs[ind]
                sent_recommendation = []
                for i in pro_po_d:
                    if i not in sent_recommendation:
                        sent_recommendation.append(i)
                # Just to print
                context = {'base': ssd, 'recommendation': sent_recommendation}

            except Page.DoesNotExist:
                context = {'base': base_uri, 'obj': "No known objects"}

            return render(request, 'suggestions.json', context)
# def KNN_regression()

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
            if "localhost:" not in object_page:
                handle_Website(object_website)
                page = handle_Page(object_website, object_page_path, object_page)
                pageobject = handle_PageObject(object_selector, object_href, object_page, object_text)
                profile_pageobject = handle_Profile_PageObject(profile, pageobject)
                handle_Profile_PageobjectLog(profile_pageobject, object_logtime)
                handle_visit(profile, object_page)
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