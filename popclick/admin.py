from django.contrib import admin
from .models import Interest, Profile, ProfileInterest
# Register your models here.

admin.site.register(Interest)
admin.site.register(ProfileInterest)
admin.site.register(Profile)