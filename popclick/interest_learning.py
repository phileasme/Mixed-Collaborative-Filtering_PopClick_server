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
    """
    Formats an array of intereests for the specified object
    Args: 
        (Profile/Pageobject) profile_or_pageobject
        (QueryObject) query_profiles_interests 
    """
    # Get all names
    interests = [i.name for i in Interest.objects.all().order_by('name')]
    # Make an array of zeros
    standardized_profile_or_pageobject_interests = [0]*(len(interests))
    # If there is no QueryObject and there the passed argument is a Profile then fetch object intjersts
    if query_profiles_interests == None:
        if profile_or_pageobject.__class__.__name__ == 'Profile':
            query_profiles_interests = ProfileInterest.objects
    # Formulated An array composed of tuples2
    if query_profiles_interests != None:
        pr_int_lvl_index = [(pi['interest'],pi['level']) for pi in query_profiles_interests.filter(profile=profile_or_pageobject).values('interest','level')]
    else:
        pr_int_lvl_index = [(pi['interest'],pi['level']) for pi in PageobjectInterest.objects.filter(pageobject=profile_or_pageobject).values('interest','level')]
    # For the specific index given by the order of the alphabetically sorted names of interests
    for it in pr_int_lvl_index:
        standardized_profile_or_pageobject_interests[interests.index(it[0])] = it[1]
    return standardized_profile_or_pageobject_interests

def learn_interests(profile, pageobject):
    """ 
    Main learning method for a given profile and knowing that the last object was interacted by more than one user
    args: 
        (Profile): profile
        (PageObject): pageobject
    """
    matrix_pageobjects_interests = []
    # Filter pro_po
    profile_pageobjects = ProfilePageobject.objects.filter(profile=profile)
    interests = [i.name for i in Interest.objects.all().order_by('name')]
    profile_formatted = get_formatted_user_or_pageobject_interests(profile)
    if not pageobject.selections == 1:
        for profile_pageobject in profile_pageobjects:
            # The profile object formulated interests for each pageobjects of the user
            formatted_po_interests = get_formatted_user_or_pageobject_interests(profile_pageobject.pageobject)
            # There is at least one value that is not a zero interest
            if not np.count_nonzero(formatted_po_interests) == 0:
                # Append to the matrix
                matrix_pageobjects_interests.append([i * profile_pageobject.selections for i in formatted_po_interests])
        # Set profile interests, calling the Neural net algorithm
        set_profile_interests(profile, runNN(matrix_pageobjects_interests, profile_formatted), interests)

def set_profile_interests(profile, new_profile_interests, interests):
    """
    Sets the interests of the user
    Args: 
        (Profile): profile
        (ProfileInterest): new_profile_interests
        (List): interests
    """
    # Learning rate
    default_learning_curve= 0.96
    # For each interests at their respectful place
    for index, interest_name in enumerate(interests):
        interest = Interest.objects.get(name=interest_name)
        # Create or get the specific interests
        profile_interest, created = ProfileInterest.objects.get_or_create(profile=profile, interest=interest)
        # Apply the rightful learning rate
        if created:
            profile_interest.level = (1-default_learning_curve)*new_profile_interests[index]
        else:
            profile_interest.level = default_learning_curve*profile_interest.level + (1-default_learning_curve)*new_profile_interests[index]
        profile_interest.save()