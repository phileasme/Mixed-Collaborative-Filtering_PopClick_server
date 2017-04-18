""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Database Model class representation file
* Location : /mainsite/popclick/models.py
"""
# Database models
from django.db import models
from django_neomodel import DjangoNode
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom)
from neomodel import config as neoconfig
from django.db import transaction, IntegrityError
# Time environment
from django.utils import timezone
import datetime
# Introduction to an encrypted field
from fernet_fields import EncryptedTextField

class Interest(models.Model):
    """
        Interest class, shows the interests of the profiles, or pageobjects
    """
    name = models.CharField(max_length=200, primary_key=True, unique=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    """
        Profile class, represents the profile of the users
    """
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
    """
        SecureAuth class, encrypted keys by fernets algorithm
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    key = EncryptedTextField()
    def __str__(self):
        return self.key

class Website(models.Model):
    """
        Website represents, the websites
    """
    host = models.CharField(unique=True, max_length=2083)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.host

class Page(models.Model):
    """
        Page class, a page which belongs to a website
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    path = models.CharField(max_length=2080)
    href = models.CharField(max_length=2083)
    profiles = models.ManyToManyField(Profile)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('website','path','href')
    def __str__(self):
        return self.href

class PageObject(models.Model):
    """
        Pageobject belongs to the pages
    """
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

class PageobjectInterest(models.Model):
    """
        Expresses the interest levels of the pageobjects
    """
    pageobject = models.ForeignKey(PageObject, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    level = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('pageobject','interest')
    def __str__(self):
        return self.pageobject.text+" "+self.interest.name

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

class PageobjectLog(models.Model):
    """
        A log addressed to the profiles, for pagobjects encounters
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    pageobject = models.ForeignKey(PageObject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.updated_at)

class Visit(models.Model):
    """
        A log addressed to the profile, page encounters
    """
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.page.href+" "+str(self.profile.id)+" "+str(self.counter)

class ProfileInterest(models.Model):
     """
        Expresses the interest levels of the profiles
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)    
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    level = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('profile','interest',)
    def __str__(self):
        return self.profile.token+' '+self.interest.name+' '+str(self.level)

class WebsiteN(StructuredNode):
    """
        Node representation of a Website
    """
    host = StringProperty(unique_index=True, required=True)
    pages = RelationshipFrom('PageN', 'IS_FROM')
    profiles = RelationshipFrom('ProfileN', 'IS_FROM')

class PageN(StructuredNode):
    """
        Node representation of a page
    """
    href = StringProperty(unique_index=True, required=True)
    profiles = RelationshipFrom('ProfileN', 'IS_FROM')
    website = RelationshipTo(WebsiteN, 'BELONGS_TO')

class ProfileN(StructuredNode):
    """
        Node representation of a profile
    """
    token = StringProperty(unique_index=True, required=True)
    website = RelationshipTo(WebsiteN, 'HAS_A_WEBSITE')
    page = RelationshipTo(PageN, 'HAS_A_PAGE')
    def get_tokens_from_common_Websites(self, page):
        results, metadata =self.cypher('START u=node({self}) MATCH (u:ProfileN)-[e:HAS_A_WEBSITE]->'+
            '(w:WebsiteN)<-[e2:HAS_A_WEBSITE]-(u2:ProfileN)-[r:HAS_A_PAGE]->(p:PageN {href:"'+page+'"})\n '+
            'RETURN u2, count(w)\n ORDER BY count(w) LIMIT 25')
        return [results]