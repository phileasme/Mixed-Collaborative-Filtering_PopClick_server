from django.contrib import admin
from .models import Website, SecureAuth, Page, Interest, Profile, ProfileInterest, PageObject, PageInterest, PageobjectInterest, ProfilePageobject, ProfilePageobjectLog 
# Register your models here.

admin.site.register(Interest)
admin.site.register(ProfileInterest)
admin.site.register(Profile)
admin.site.register(Website)
admin.site.register(PageObject)
admin.site.register(Page)
admin.site.register(ProfilePageobject)
admin.site.register(SecureAuth)