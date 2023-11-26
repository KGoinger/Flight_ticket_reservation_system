from django.contrib import admin

# Register your models here.

from .models import UserProfile
#做一个测试
admin.site.register(UserProfile)
