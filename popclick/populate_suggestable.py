from .models import Interest, Visit, Website, Page, Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 
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

def handle_PageobjectLog(profile, pageobject):
    pageobject_log = PageobjectLog(profile=profile, pageobject=pageobject)
    pageobject_log.save()

def handle_visit(profile, page):
    try:
        Page.objects.get(href=page)
        page = Page.objects.get(href=page)
        visit = Visit(profile=profile, page=page)
        visit.save()
    except Page.DoesNotExist:
        page = None

