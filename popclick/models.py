import datetime

from django.db import models
from django.utils import timezone
from fernet_fields import EncryptedTextField
from django_neomodel import DjangoNode
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom)# Models are underneath
from neomodel import config as neoconfig

neoconfig.DATABASE_URL = 'bolt://admin:totalrecall@localhost:7687'

class Interest(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    age = models.IntegerField(default=0)
    token = models.CharField(unique=True, max_length=200)
    logtime = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=20, default=None)
    interests = models.ManyToManyField(Interest, through='ProfileInterest')
    activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.token

class SecureAuth(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    key = EncryptedTextField()
    def __str__(self):
        return self.key

class Website(models.Model):
    host = models.CharField(unique=True, max_length=2083)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.host

class Page(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    path = models.CharField(max_length=2080)
    href = models.CharField(unique=True, max_length=2083)
    profiles = models.ManyToManyField(Profile)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.href

class PageObject(models.Model):
    selector = models.CharField(max_length=5000)
    href = models.CharField(max_length=2083)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    text = models.CharField(max_length=3000)
    selections = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('page','href','selector')
    def __str__(self):
        return self.page.href+" "+self.text

class ProfilePageobject(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    pageobject = models.ForeignKey(PageObject, on_delete=models.CASCADE)
    selections = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('profile','pageobject',)
    def __str__(self):
        return self.profile.token+" "+self.pageobject.text+" "+self.pageobject.href+" "+str(self.selections)
class ProfilePageobjectLog(models.Model):
    profile_pageobject = models.ForeignKey(ProfilePageobject, on_delete=models.CASCADE)
    logtime = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.logtime)
class Visit(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.page.href+" "+str(self.profile.id)+" "+str(self.counter)

class ProfileInterest(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)    
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('profile','interest',)
    def __str__(self):
        return self.profile.token+' '+self.interest.name+' '+str(self.level)

class PageInterest(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    counter = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('page','interest',)

class PageobjectInterest(models.Model):
    pageobject = models.ForeignKey(Profile, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    counter = models.IntegerField(default=1)
    class Meta:
        unique_together = ('pageobject','interest',)
    def __str__(self):
        return self.pageobject.href+' '+self.interest.name+' '+str(self.counter)

class WebsiteN(StructuredNode):
    host = StringProperty(unique_index=True, required=True)
    pages = RelationshipFrom('PageN', 'IS_FROM')
    profiles = RelationshipFrom('ProfileN', 'IS_FROM')
class PageN(StructuredNode):
    href = StringProperty(unique_index=True, required=True)
    profiles = RelationshipFrom('ProfileN', 'IS_FROM')
    website = RelationshipTo(WebsiteN, 'BELONGS_TO')
class ProfileN(StructuredNode):
    token = StringProperty(unique_index=True, required=True)
    website = RelationshipTo(WebsiteN, 'HAS_A_WEBSITE')
    page = RelationshipTo(PageN, 'HAS_A_PAGE')