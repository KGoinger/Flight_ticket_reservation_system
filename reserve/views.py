from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Flight,Order
from django.utils import timezone
from .models import UserProfile
from django.utils.dateparse import parse_date
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')


def search(request):
    if request.method == 'POST':
        departure_city = request.POST.get('departure_city')
        arrival_city = request.POST.get('arrival_city')
        departure_date_str = request.POST.get('departure_date')

        # 将字符串格式的日期转换为日期对象
        departure_date = parse_date(departure_date_str)
        #print(departure_date)
        # 在查询中只比较日期部分
        flights = Flight.objects.filter(
            departure=departure_city,
            destination=arrival_city,
            departure_time__date=departure_date
        )
        #print("QuerySet:", flights.query)  # 打印 SQL 查询

        return render(request, 'search.html', {'flights': flights})

    # 如果不是 POST 请求，可以重定向到首页或者显示错误消息
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 或其他适合的重定向
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

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

@login_required(login_url='/login/')
def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    if request.method == 'POST':
        # 这里假设用户已经登录并且request.user是当前登录用户
        user = request.user

        # 创建订单
        order = Order(
            user=user,
            flight=flight,
            booking_time=timezone.now(),  # 使用Django的timezone模块来获取当前时间
            order_status='成功'  # 假设初始状态为“成功”
        )
        order.save()

        # 可以重定向到一个新的页面，比如订单详情页面或预订确认页面
        return redirect('order_details', order_id=order.id)

    return render(request, 'book_ticket.html', {'flight': flight})