from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("这里是liujiangblog.com的投票站点")


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # username, email=None, password=None, **extra_fields
        user = User.objects.create_user(username=username, password=password)
        user.save()
        if user:
            auth.login(request, user)

    return render(request, 'register.html')
