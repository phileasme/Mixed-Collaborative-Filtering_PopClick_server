import datetime

from django.db import models
from django.utils import timezone
# Create your models here.

class Interest(models.Model):
	name = models.CharField(max_length=200, primary_key=True)

class Profile(models.Model):
	age = models.IntegerField(default=0)
	token = models.CharField(unique=True, max_length=200)
	auth = models.CharField(max_length=530)
	logtime = models.DateTimeField(auto_now=True)
	gender = models.CharField(max_length=20, default=None)
	interests = models.ManyToManyField(Interest, through='ProfileInterest')
	def __str__(self):
		return self.token

class Website(models.Model):
	host = models.CharField(unique=True, max_length=2083)
	def __str__(self):
		return self.host

class Page(models.Model):
	website = models.ForeignKey(Website, on_delete=models.CASCADE)
	path = models.CharField(max_length=2080)
	href = models.CharField(unique=True, max_length=2083)
	profiles = models.ManyToManyField(Profile)
	def __str__(self):
		return self.href

class PageObject(models.Model):
	selector = models.CharField(max_length=5000)
	page = models.ForeignKey(Page, on_delete=models.CASCADE)
	text = models.CharField(max_length=3000)
	
class ProfilePageobject(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	pageobject = models.ForeignKey(PageObject, on_delete=models.CASCADE)
	selections = models.IntegerField(default=0)
	class Meta:
		unique_together = ('profile','pageobject',)
		
class PageobjectLog(models.Model):
	profile_pageobject = models.ForeignKey(ProfilePageobject, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now=True)

class Visit(models.Model):
	page = models.ForeignKey(Page, on_delete=models.CASCADE)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	counter = models.IntegerField(default=0)
	updated = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.page.href+" "+self.profile.id+" "+self.counter

class ProfileInterest(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)	
	interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
	level = models.IntegerField(default=1)

class PageInterest(models.Model):
	page = models.ForeignKey(Page, on_delete=models.CASCADE)
	interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
	counter = models.IntegerField(default=1)
	class Meta:
		unique_together = ('page','interest',)
