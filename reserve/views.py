from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("主页")


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # username, email=None, password=None, **extra_fields
        user = User.objects.create_user(username=username, password=password)
        user.save()
        if user:
            #todo这里要不要去掉auth.login()
            auth.login(request, user)
            return redirect('login')  # 注册成功后跳转至登录

    return render(request, 'register.html')

'''    用户登录'''
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)  #这里做了登录
            if user.is_superuser:
                return redirect('finance')
            else:
                return redirect('userprofile')  # 跳转至首页
    return render(request, "login.html")

@login_required(login_url='/login/')
def userprofile(request):
    name = request.user.username
    return render(request, 'userprofile.html', {'name': name})

def logout(request):
    auth.logout(request)
    return redirect('login')  # 退出后，页面跳转至登录界面
@login_required(login_url='/login/')
def finance(request):
    name = request.user.username
    return render(request, 'finance.html', {'name': name})