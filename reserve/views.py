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
from django.db.models import F
from django.db.models import Sum
from datetime import timedelta


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
    orders = Order.objects.filter(user=request.user,order_status='成功')
    return render(request, 'userprofile.html', {'orders': orders})

def logout(request):
    auth.logout(request)
    return redirect('login')  # 退出后，页面跳转至登录界面
@login_required(login_url='/login/')
def finance(request):
    # 获取所有订单
    orders = Order.objects.all()

    # 将订单传递给模板
    return render(request, 'finance.html', {'orders': orders})

@login_required(login_url='/login/')
def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    user_profile = UserProfile.objects.get(user=request.user)
    remaining_seats = flight.capacity - flight.book_sum

    if request.method == 'POST':
        print("ok")
        # 检查余票
        if flight.book_sum >= flight.capacity:
            # 处理没有余票的情况
            return render(request, 'book_ticket.html', {
                'flight': flight,
                'error': '对不起，该航班已无余票。'
            })

        # 检查用户余额是否足够
        if user_profile.balance < flight.price:
            # 处理余额不足的情况
            return render(request, 'book_ticket.html', {
                'flight': flight,
                'error': '余额不足，请充值后再预订。',
                'remaining_seats': remaining_seats
            })

        # 扣除用户余额
        user_profile.balance -= flight.price
        user_profile.save()

        # 更新航班预订数
        Flight.objects.filter(pk=flight_id).update(book_sum=F('book_sum') + 1)

        # 创建订单
        order = Order(
            user=request.user,
            flight=flight,
            booking_time=timezone.now(),
            order_status='成功'
        )
        order.save()

        # 重定向到用户个人资料页面
        return redirect('userprofile')

    return render(request, 'book_ticket.html', {'flight': flight,'remaining_seats': remaining_seats})

def cancel_order(request,order_id):
    # 缺少检查：只有起飞时间大于当前时间才能退票
    # 获取订单对象，确保只有订单的所有者才能退票
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    # 检查订单状态和航班起飞时间
    if order.order_status != '成功' or order.flight.departure_time <= timezone.now():
        # 如果订单不是“成功”状态或航班已起飞，处理错误情况
        return HttpResponse("非法退票操作")  # 请替换为适当的错误处理

    # 归还用户的余额
    user_profile = UserProfile.objects.get(user=order.user)
    user_profile.balance += order.flight.price
    user_profile.save()

    # 减少已预订的座位数
    Flight.objects.filter(pk=order.flight.id).update(book_sum=F('book_sum') - 1)

    # 更新订单状态为“退票”
    order.order_status = '退票'
    order.save()

    # 重定向到用户主页
    return redirect('userprofile')