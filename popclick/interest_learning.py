""" 
* ©Copyrights, all rights reserved at the exception of the mentioned 3rd party libraries.
* @author: Phileas Hocquard 
* Profile Learning, Interests formatting
* Location : /mainsite/popclick/interest_learning.py
"""
# Database models
from .models import Interest, PageobjectInterest, Visit, Website, SecureAuth, Page, Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 
# Operations / Third party
import numpy as np
from numpy import exp, array, random, dot
# External file import
from popclick.neural_network_interests import *

def get_formatted_user_or_pageobject_interests(profile_or_pageobject, query_profiles_interests=None):
    interests = [i.name for i in Interest.objects.all().order_by('name')]
    standardized_profile_or_pageobject_interests = [0]*(len(interests))
    if query_profiles_interests == None:
        if profile_or_pageobject.__class__.__name__ == 'Profile':
            query_profiles_interests = ProfileInterest.objects

    if query_profiles_interests != None:
        pr_int_lvl_index = [(pi['interest'],pi['level']) for pi in query_profiles_interests.filter(profile=profile_or_pageobject).values('interest','level')]
    else:
        pr_int_lvl_index = [(pi['interest'],pi['level']) for pi in PageobjectInterest.objects.filter(pageobject=profile_or_pageobject).values('interest','level')]
    for it in pr_int_lvl_index:
        standardized_profile_or_pageobject_interests[interests.index(it[0])] = it[1]
    return standardized_profile_or_pageobject_interests

def learn_interests(profile, pageobject):
    matrix_pageobjects_interests = []
    profile_pageobjects = ProfilePageobject.objects.filter(profile=profile)
    interests = [i.name for i in Interest.objects.all().order_by('name')]
    profile_formatted = get_formatted_user_or_pageobject_interests(profile)
    if not pageobject.selections == 1:
        for profile_pageobject in profile_pageobjects:
            formatted_po_interests = get_formatted_user_or_pageobject_interests(profile_pageobject.pageobject)
            if not np.count_nonzero(formatted_po_interests) == 0:
                matrix_pageobjects_interests.append([i * profile_pageobject.selections for i in formatted_po_interests])
        set_profile_interests(profile, runNN(matrix_pageobjects_interests, profile_formatted), interests)

def set_profile_interests(profile, new_profile_interests, interests):
    default_learning_curve= 0.96
    for index, interest_name in enumerate(interests):
        interest = Interest.objects.get(name=interest_name)
        profile_interest, created = ProfileInterest.objects.get_or_create(profile=profile, interest=interest)
        if created:
            profile_interest.level = (1-default_learning_curve)*new_profile_interests[index]
        else:
            profile_interest.level = default_learning_curve*profile_interest.level + (1-default_learning_curve)*new_profile_interests[index]
        profile_interest.save()