from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Flight, Order
from django.utils import timezone
from .models import UserProfile
from django.utils.dateparse import parse_date
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.db.models import Sum
from datetime import timedelta, datetime
from operator import attrgetter
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse

from pyecharts.charts import Bar
from pyecharts import options as opts

def create_financial_chart(weekly_income, monthly_income, yearly_income):
    bar = Bar()
    bar.add_xaxis(["周收入", "月收入", "年收入"])
    bar.add_yaxis("收入", [weekly_income, monthly_income, yearly_income])
    bar.set_global_opts(title_opts=opts.TitleOpts(title="收入图表"))
    return bar

def index(request):
    return render(request, 'index.html')


# def search(request):
#     print("hello_world")
#     if request.method == 'POST':
#         departure_city = request.POST.get('departure_city')
#         arrival_city = request.POST.get('arrival_city')
#         departure_date_str = request.POST.get('departure_date')
#
#         if not departure_city or not arrival_city or not departure_date_str:
#             messages.warning(request, '请填写所有字段。')
#             return redirect('index')
#
#         departure_date = parse_date(departure_date_str)
#
#         flights = Flight.objects.filter(
#             departure=departure_city,
#             destination=arrival_city,
#             departure_time__date=departure_date
#         ).order_by('departure_time')
#         print({
#             'departure_city': departure_city,
#             'arrival_city': arrival_city,
#             'departure_date': departure_date,
#             'flights': flights})
#         return render(request, 'search.html', {
#             'departure_city': departure_city,
#             'arrival_city': arrival_city,
#             'departure_date': departure_date,
#             'flights': flights})
#     else:
#         return render(request, 'search.html')


def search(request):
    if request.method == 'POST':
        button_clicked = request.POST.get('button_clicked')
        last_button_clicked = request.session.get('last_button_clicked', 'departure_time_asc')

        departure_city = request.POST.get('departure_city')
        arrival_city = request.POST.get('arrival_city')
        departure_date_str = request.POST.get('departure_date')

        if not departure_city or not arrival_city or not departure_date_str:
            messages.warning(request, '请填写所有字段。')
            return redirect('index')

        # 将字符串格式的日期转换为日期对象
        departure_date = parse_date(departure_date_str)

        request.session['departure_city'] = departure_city
        request.session['arrival_city'] = arrival_city
        request.session['departure_date'] = departure_date_str


        flights = Flight.objects.filter(
            departure=departure_city,
            destination=arrival_city,
            departure_time__date=departure_date
        ).order_by('departure_time')
        for flight in flights:
            flight.save()


        if button_clicked != last_button_clicked:
            request.session['last_button_clicked'] = button_clicked

        if button_clicked == '起飞时间早-晚' and last_button_clicked != '起飞时间早-晚':
            flights = flights.order_by('departure_time')
            button_highlight = '起飞时间早-晚'
        elif button_clicked == '到达时间早-晚' and last_button_clicked != '到达时间早-晚':
            flights = flights.order_by('arrival_time')
            button_highlight = '到达时间早-晚'
        elif button_clicked == '低价优先' and last_button_clicked != '低价优先':
            flights = flights.order_by('price')
            button_highlight = '低价优先'
        elif button_clicked == '耗时短优先' and last_button_clicked != '耗时短优先':
            flights = flights.order_by('duration')
            button_highlight = '耗时短优先'
        else:
            button_highlight = last_button_clicked

        return render(request, 'search.html', {
            'flights': flights,
            'departure_city': departure_city,
            'arrival_city': arrival_city,
            'departure_date': departure_date,
            'button_highlight': button_highlight
        })

    else:
        departure_city = request.session.get('departure_city', '')
        arrival_city = request.session.get('arrival_city', '')
        departure_date_str = request.session.get('departure_date', '')

        if not departure_city or not arrival_city or not departure_date_str:
            return render(request, 'search.html')

        departure_date = parse_date(departure_date_str)

        flights = Flight.objects.filter(
            departure=departure_city,
            destination=arrival_city,
            departure_time__date=departure_date
        )

        last_button_clicked = request.session.get('last_button_clicked', '起飞时间早-晚')

        if last_button_clicked == '起飞时间早-晚':
            flights = flights.order_by('departure_time')
        elif last_button_clicked == '到达时间早-晚':
            flights = flights.order_by('arrival_time')
        elif last_button_clicked == '低价优先':
            flights = flights.order_by('price')
        elif last_button_clicked == '耗时短优先':
            flights = flights.order_by('duration')

        return render(request, 'search.html', {
            'departure_city': departure_city,
            'arrival_city': arrival_city,
            'departure_date': departure_date,
            'flights': flights,
            'button_highlight': last_button_clicked
        })


# def search(request):
#     if request.method == 'POST':
#         departure_city = request.POST.get('departure_city')
#         arrival_city = request.POST.get('arrival_city')
#         departure_date_str = request.POST.get('departure_date')
#
#         # 将字符串格式的日期转换为日期对象
#         departure_date = parse_date(departure_date_str)
#         #print(departure_date)
#         # 在查询中只比较日期部分
#         flights = Flight.objects.filter(
#             departure=departure_city,
#             destination=arrival_city,
#             departure_time__date=departure_date
#         )
#         #print("QuerySet:", flights.query)  # 打印 SQL 查询
#
#         return render(request, 'search.html', {'flights': flights})
#
#     # 如果不是 POST 请求，可以重定向到首页或者显示错误消息
#     return redirect('index')
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
            auth.login(request, user)  # 这里做了登录
            if user.is_superuser:
                return redirect('finance')
            else:
                return redirect('userprofile')  # 跳转至首页
    return render(request, "login.html")


@login_required(login_url='/login/')
def userprofile(request):
    orders = Order.objects.filter(user=request.user, order_status='成功')
    return render(request, 'userprofile.html', {'orders': orders})


def logout(request):
    auth.logout(request)
    return redirect('login')  # 退出后，页面跳转至登录界面


@login_required(login_url='/login/')
def finance(request):
    # 获取所有订单
    orders = Order.objects.all()
    current_time = timezone.now()

    # 计算不同时间段的收入和退票金额
    def calculate_financial_data(start_date):
        data = Order.objects.filter(booking_time__gte=start_date)
        total_income = data.aggregate(Sum('flight__price'))['flight__price__sum'] or 0
        total_refunds = data.filter(order_status='退票').aggregate(Sum('flight__price'))['flight__price__sum'] or 0
        profit = total_income - total_refunds
        return data.count(), total_income, total_refunds, profit

    # 计算周收入
    week_ago = current_time - timedelta(days=7)
    weekly_flights, weekly_income, weekly_refunds, weekly_profit = calculate_financial_data(week_ago)

    # 计算月收入
    month_ago = current_time - timedelta(days=30)
    monthly_flights, monthly_income, monthly_refunds, monthly_profit = calculate_financial_data(month_ago)

    # 计算年收入
    year_ago = current_time - timedelta(days=365)
    yearly_flights, yearly_income, yearly_refunds, yearly_profit = calculate_financial_data(year_ago)

    # 创建图表
    chart = create_financial_chart(weekly_income, monthly_income, yearly_income)
    chart_html = chart.render_embed()
    return render(request, 'finance.html', {
        'orders': orders,
        'weekly_flights': weekly_flights,
        'weekly_income': weekly_income,
        'weekly_refunds': weekly_refunds,
        'weekly_profit': weekly_profit,
        'monthly_flights': monthly_flights,
        'monthly_income': monthly_income,
        'monthly_refunds': monthly_refunds,
        'monthly_profit': monthly_profit,
        'yearly_flights': yearly_flights,
        'yearly_income': yearly_income,
        'yearly_refunds': yearly_refunds,
        'yearly_profit': yearly_profit,
        'chart_html': chart_html
    })


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

    return render(request, 'book_ticket.html', {'flight': flight, 'remaining_seats': remaining_seats})


def cancel_order(request, order_id):
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

def recharge(request):
    money = int(request.POST.get('money'))
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.balance += money
    user_profile.save()
    return redirect('userprofile')
