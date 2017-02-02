from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
import datetime
from django.utils import timezone
from .models import Prime
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json as jamison
from Crypto.Util import number
from random import randint

def generate_all_primes():
	count = Prime.objects.count()
	if count < 100:
		for _ in range(100-count):
			nb = str(number.getPrime(1024))
			prime = Prime.objects.create(number=nb)
			prime.save()

class IndexView(generic.ListView):
	template_name = 'generator/index.html'
	context_object_name = 'latest_primes_list'
	generate_all_primes()
	def get_queryset(self):
		return Prime.objects.all()

