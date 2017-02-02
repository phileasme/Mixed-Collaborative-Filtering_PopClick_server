from django.db import models
from django.db.models.fields import IntegerField
from django.conf import settings


# Create your models here.
class Prime(models.Model):
	number = models.CharField(max_length=1000)
	uses = models.IntegerField(default=0)
	def _str_(self):
		return self.number
		