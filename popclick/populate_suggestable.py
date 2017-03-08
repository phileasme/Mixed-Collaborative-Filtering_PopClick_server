from .models import Interest, Visit, Website, Page, Profile, ProfileInterest, PageObject, PageInterest, PageobjectInterest, ProfilePageobject, ProfilePageobjectLog 
def handle_Website(host):
    website, created = Website.objects.get_or_create(host=host)
    return website

def handle_Page(host, path, href):
    website, created = Website.objects.get_or_create(host=host)
    page, cr = Page.objects.get_or_create(path=path, href=href, website=website)
    return page
# Handle unique violation
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

