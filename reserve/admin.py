from django.contrib import admin

# Register your models here.

from .models import UserProfile
from .models import Flight
#做一个测试
admin.site.register(Flight)