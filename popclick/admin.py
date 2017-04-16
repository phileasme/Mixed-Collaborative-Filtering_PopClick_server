""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Used for the administrators portal
"""

from django.contrib import admin
# Database models
from .models import Website, SecureAuth, Page, PageobjectInterest, Interest, Profile
from .models import ProfileInterest, PageObject, ProfilePageobject, PageobjectLog
# Registerating models to supervise as an administrator
admin.site.register(Interest)
admin.site.register(ProfileInterest)
admin.site.register(Profile)
admin.site.register(Website)
admin.site.register(PageObject)
admin.site.register(Page)
admin.site.register(ProfilePageobject)
admin.site.register(SecureAuth)
admin.site.register(PageobjectLog)
admin.site.register(PageobjectInterest)