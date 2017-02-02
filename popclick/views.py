from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
import random
from django.core import serializers
from datetime import datetime
import requests
import json
from .models import User, Interest, UserInterest

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = request.POST
        if 'age' in data:
            new_user = User(
            		age=data['age'], 
            		token=randToken(),
            		auth=randToken(),
            		logtime=datetime.strptime(data['logtime'], r'%Y-%m-%d %H:%M'))
            new_user.save()
            for interest in data['interests']:
            	new_interest = Interest(name=interest)
            	new_interest.save()
            	new_user_interest = UserInterest(user=new_user, interest=new_interest)
            	new_user_interest.save()
            context = { 'user' : new_user }
            return render(request, 'create_user.json', context)

# def details(request, token):
#     event = Event.objects.get(token=token)
#     positions = Position.objects.filter(event=event).order_by('timestamp', 'pk')
#     context = {'event' : event, 'positions' : positions}
#     return render(request, 'event_details.json', context)

def randToken():
    a = '0123456789abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ'
    return "".join([random.choice(a) for _ in range(20)])