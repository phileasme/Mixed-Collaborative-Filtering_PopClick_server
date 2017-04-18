from .models import Interest, Visit, PageobjectInterest, Website, Page
from .models import Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 

def handle_Website(host):
    """
        Gets an existing website or creates the a website
        Args: (String) host
    """
    website, created = Website.objects.get_or_create(host=host)
    return website

def handle_Page(host, path, href):
    """
        Gets an existing page or creates it.
        Args: (String) host
              (String) path
              (String) hreft
    """ 
    website, created = Website.objects.get_or_create(host=host)
    page, cr = Page.objects.get_or_create(path=path, href=href, website=website)
    return page
    
def handle_PageObject(selector, href, page, text):
    """
        Greats or retreive page object, in all casses incremente selections
        Args: (String) selector,href,page,text
    """
    page= Page.objects.get(href=page)
    pageobject, created = PageObject.objects.get_or_create(selector=selector, href=href, page=page)
    pageobject.text= text
    pageobject.selections += 1 
    pageobject.save()
    return pageobject

def handle_Profile_PageObject(profile, pageobject):
    """
        increments the number of selections
        (PageObject) : pageobject
        (Profile)   : profile
    """
    new_profile_pageobject, created = ProfilePageobject.objects.get_or_create(profile=profile, pageobject=pageobject)
    new_profile_pageobject.selections += 1
    new_profile_pageobject.save()
    return new_profile_pageobject

def handle_PageobjectLog(profile, pageobject):
    """
        creates a new log for pageobjects
        (PageObject) : pageobject
        (Profile)   : profile
    """
    pageobject_log= PageobjectLog(profile=profile, pageobject=pageobject)
    pageobject_log.save()

def handle_visit(profile, page):
    """
    Creates a new visit for the user
        (Page) : page
        (Profile) : profile
    """
    try:
        Page.objects.get(href=page)
        page= Page.objects.get(href=page)
        visit= Visit(profile=profile, page=page)
        visit.save()
    except Page.DoesNotExist:
        page = None

def pageobject_interests_update(interests, pageobjects, pageobject_interests):
    """
        Simularly to profiles,
        Update the interests of the pageobjects
    """
    for index, po in enumerate(pageobjects):
        # for inter in interests:
        for index_inter, inter in enumerate(pageobject_interests[index]):
            current_int= Interest.objects.get(name=interests[index_inter])
            pageobject_interest, created = PageobjectInterest.objects.get_or_create(pageobject=po, interest=current_int)
            pageobject_interest.level= inter
            pageobject_interest.save()