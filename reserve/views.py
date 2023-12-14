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
from django.db import transaction
from django.db.models import Q

# Create your views here.
from django.http import HttpResponse

from pyecharts.charts import Bar
from pyecharts import options as opts

def search_transfer_flights(departure_city, arrival_city, departure_date):
    transfer_flights = []

    # 第一段航班：从出发城市到任何其他城市
    first_leg_flights = Flight.objects.filter(
        departure=departure_city,
        departure_time__date=departure_date
    )

    # 对于每一段第一段航班，找到可能的第二段航班
    for first_leg in first_leg_flights:
        # 第二段航班的最早起飞时间（考虑到换乘时间）
        earliest_departure_time = first_leg.arrival_time

        # 第二段航班：从第一段航班的目的地到最终目的地
        second_leg_flights = Flight.objects.filter(
            departure=first_leg.destination,
            destination=arrival_city,
            departure_time__gt=earliest_departure_time
        )

        for second_leg in second_leg_flights:
            # total_price = first_leg.economy_class_price + second_leg.economy_class_price
            total_duration = second_leg.arrival_time - first_leg.departure_time
            transfer_flights.append({
                'first_leg': first_leg,
                'second_leg': second_leg,
                # 'total_price': total_price,
                'total_duration': total_duration
            })

    return transfer_flights

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


        transfer_flights = []
        transfer_flights = search_transfer_flights(departure_city, arrival_city, departure_date)
        print(transfer_flights)
        
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
            'transfer_flights': transfer_flights,  # 中转航班
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
    #只有管理员才可以访问
    if not request.user.is_superuser:
        return redirect('userprofile')
    # 获取所有订单
    orders = Order.objects.all()
    current_time = timezone.now()

    # # 计算不同时间段的收入和退票金额
    # def calculate_financial_data(start_date):
    #     data = Order.objects.filter(booking_time__gte=start_date)
    #     total_income = data.aggregate(Sum('flight__price'))['flight__price__sum'] or 0
    #     total_refunds = data.filter(order_status='退票').aggregate(Sum('flight__price'))['flight__price__sum'] or 0
    #     profit = total_income - total_refunds
    #     return data.count(), total_income, total_refunds, profit
    # 计算不同时间段的航班数量、收入、退票金额和利润
    # def calculate_financial_data(start_date):
    #     # 获取特定时间段内的独立航班
    #     flights_in_period = Flight.objects.filter(departure_time__gte=start_date, departure_time__lte=current_time).distinct()
        
    #     # 获取这些航班相关的所有订单
    #     orders_in_period = Order.objects.filter(flight_id__in=flights_in_period.values_list('id', flat=True))
        
    #     # 计算总收入和退票金额
    #     total_income = orders_in_period.aggregate(Sum('flight__price'))['flight__price__sum'] or 0
    #     total_refunds = orders_in_period.filter(order_status='退票').aggregate(Sum('flight__price'))['flight__price__sum'] or 0
    #     profit = total_income - total_refunds

    #     # 返回独立航班数、总收入、退票金额和利润
    #     return flights_in_period.count(), total_income, total_refunds, profit
    def calculate_financial_data(start_date):
        current_time = timezone.now()
        
        # 获取在特定时间段内且有“成功”订单的独立航班
        flights_in_period = Flight.objects.filter(
            departure_time__gte=start_date,
            departure_time__lte=current_time,
            order__order_status='成功'
        ).distinct()

        # 获取这些航班相关的所有订单
        orders_in_period = Order.objects.filter(
            flight_id__in=flights_in_period.values_list('id', flat=True)
        )
        
        # 计算总收入和退票金额
        total_income = orders_in_period.aggregate(Sum('flight__price'))['flight__price__sum'] or 0
        total_refunds = orders_in_period.filter(order_status='退票').aggregate(Sum('flight__price'))['flight__price__sum'] or 0
        profit = total_income - total_refunds

        return flights_in_period.count(), total_income, total_refunds, profit

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
    chart = create_financial_chart(weekly_profit, monthly_profit, yearly_profit)
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
@transaction.atomic
def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight.objects.select_for_update(), pk=flight_id)
    user_profile = UserProfile.objects.select_for_update().get(user=request.user)
    first_class_remaining_seats = flight.first_class_capacity - flight.first_class_book_sum
    economy_class_remaining_seats = flight.economy_class_capacity - flight.economy_class_book_sum

    if request.method == 'POST':
        class_type = request.POST.get('class_type')
        if Order.objects.filter(user=request.user, flight=flight).exists():
            return HttpResponse("请勿重复预订")

        if class_type == 'first_class':
            if flight.first_class_book_sum >= flight.first_class_capacity:
                return render(request, 'book_ticket.html', {
                    'flight': flight,
                    'error': '对不起，该航班头等舱已无余票。'
                })
            if user_profile.balance < flight.first_class_price:
                return render(request, 'book_ticket.html', {
                    'flight': flight,
                    'error': '余额不足，请充值后再预订。',
                    'remaining_seats': first_class_remaining_seats
                })
            user_profile.balance -= flight.first_class_price
            user_profile.save()
            Flight.objects.filter(pk=flight_id).update(first_class_book_sum=F('first_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=flight,
                booking_time=timezone.now(),
                class_type='first_class',
                price=flight.first_class_price,
                order_status='成功'
            )
            order.save()
            return redirect('userprofile')

        elif class_type == 'economy_class':
            if flight.economy_class_book_sum >= flight.economy_class_capacity:
                return render(request, 'book_ticket.html', {
                    'flight': flight,
                    'error': '对不起，该航班经济舱已无余票。'
                })
            if user_profile.balance < flight.economy_class_price:
                return render(request, 'book_ticket.html', {
                    'flight': flight,
                    'error': '余额不足，请充值后再预订。',
                    'remaining_seats': economy_class_remaining_seats
                })
            user_profile.balance -= flight.economy_class_price
            user_profile.save()
            Flight.objects.filter(pk=flight_id).update(economy_class_book_sum=F('economy_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=flight,
                booking_time=timezone.now(),
                class_type='economy_class',
                price=flight.economy_class_price,
                order_status='成功'
            )
            order.save()
            return redirect('userprofile')

    return render(request, 'book_ticket.html', {'flight': flight,
                                                'first_class_remaining_seats': first_class_remaining_seats,
                                                'economy_class_remaining_seats': economy_class_remaining_seats})


@login_required(login_url='/login/')
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(Order.objects.select_for_update(), pk=order_id, user=request.user)

    if order.order_status != '成功' or order.flight.departure_time <= timezone.now():
        return HttpResponse("非法退票操作")

    user_profile = UserProfile.objects.select_for_update().get(user=order.user)
    user_profile.balance += order.price
    user_profile.save()
    if order.class_type == 'first_class':
        Flight.objects.filter(pk=order.flight.id).update(first_class_book_sum=F('first_class_book_sum') - 1)
    elif order.class_type == 'economy_class':
        Flight.objects.filter(pk=order.flight.id).update(economy_class_book_sum=F('economy_class_book_sum') - 1)

    order.order_status = '退票'
    order.save()

    return redirect('userprofile')

def recharge(request):
    money = int(request.POST.get('money'))
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.balance += money
    user_profile.save()
    return redirect('userprofile')


@login_required(login_url='/login/')
@transaction.atomic
def book_transfer_ticket(request, first_leg_id, second_leg_id):
    first_leg = get_object_or_404(Flight, pk=first_leg_id)
    second_leg = get_object_or_404(Flight, pk=second_leg_id)
    user_profile = UserProfile.objects.get(user=request.user)
    first_leg_first_class_remaining_seats = first_leg.first_class_capacity - first_leg.first_class_book_sum
    first_leg_economy_class_remaining_seats = first_leg.economy_class_capacity - first_leg.economy_class_book_sum
    second_leg_first_class_remaining_seats = second_leg.first_class_capacity - second_leg.first_class_book_sum
    second_leg_economy_class_remaining_seats = second_leg.economy_class_capacity - second_leg.economy_class_book_sum

    if request.method == 'POST':
        first_leg_class_type = request.POST.get('first_leg_class_type')
        second_leg_class_type = request.POST.get('second_leg_class_type')
        total_price = first_leg.get_price_by_class(first_leg_class_type) + second_leg.get_price_by_class(second_leg_class_type)

        if first_leg_class_type == 'first_class':
            if first_leg.first_class_book_sum >= first_leg.first_class_capacity:
                return render(request, 'book_transfer_ticket.html', {
                    'first_leg': first_leg,
                    'second_leg': second_leg,
                    'error': '对不起，第一段航班头等舱已无余票。'
                })
        elif first_leg_class_type == 'economy_class':
            if first_leg.economy_class_book_sum >= first_leg.economy_class_capacity:
                return render(request, 'book_transfer_ticket.html', {
                    'first_leg': first_leg,
                    'second_leg': second_leg,
                    'error': '对不起，第一段航班经济舱已无余票。'
                })
        if second_leg_class_type == 'first_class':
            if second_leg.first_class_book_sum >= second_leg.first_class_capacity:
                return render(request, 'book_transfer_ticket.html', {
                    'first_leg': first_leg,
                    'second_leg': second_leg,
                    'error': '对不起，第二段航班头等舱已无余票。'
                })
        elif second_leg_class_type == 'economy_class':
            if second_leg.economy_class_book_sum >= second_leg.economy_class_capacity:
                return render(request, 'book_transfer_ticket.html', {
                    'first_leg': first_leg,
                    'second_leg': second_leg,
                    'error': '对不起，第二段航班经济舱已无余票。'
                })

        if user_profile.balance < total_price:
            return render(request, 'book_transfer_ticket.html', {
                'error': '余额不足，请充值后再预订。',
                'first_leg': first_leg,
                'second_leg': second_leg,
            })

        # 扣除用户余额
        user_profile.balance -= total_price
        user_profile.save()
        print('扣除用户余额成功')
        if first_leg_class_type == 'first_class':
            # 更新航班的头等舱已订票数
            Flight.objects.filter(pk=first_leg.id).update(first_class_book_sum=F('first_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=first_leg,
                booking_time=timezone.now(),
                class_type='first_class',
                price=first_leg.first_class_price,
                order_status='成功'
            )
            order.save()

        elif first_leg_class_type == 'economy_class':
            # 更新航班的经济舱已订票数
            Flight.objects.filter(pk=first_leg.id).update(economy_class_book_sum=F('economy_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=first_leg,
                booking_time=timezone.now(),
                class_type='economy_class',
                price=first_leg.economy_class_price,
                order_status='成功'
            )
            order.save()
        if second_leg_class_type == 'first_class':
            # 更新航班的头等舱已订票数
            Flight.objects.filter(pk=second_leg.id).update(first_class_book_sum=F('first_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=second_leg,
                booking_time=timezone.now(),
                class_type='first_class',
                price=second_leg.first_class_price,
                order_status='成功'
            )
            order.save()
        elif second_leg_class_type == 'economy_class':
            # 更新航班的经济舱已订票数
            Flight.objects.filter(pk=second_leg.id).update(economy_class_book_sum=F('economy_class_book_sum') + 1)
            order = Order(
                user=request.user,
                flight=second_leg,
                booking_time=timezone.now(),
                class_type='economy_class',
                price=second_leg.economy_class_price,
                order_status='成功'
            )
            order.save()
        return redirect('userprofile')

    return render(request, 'book_transfer_ticket.html', {'first_leg': first_leg,
                                                         'second_leg': second_leg,
                                                         'first_leg_first_class_remaining_seats': first_leg_first_class_remaining_seats,
                                                         'first_leg_economy_class_remaining_seats': first_leg_economy_class_remaining_seats,
                                                         'second_leg_first_class_remaining_seats': second_leg_first_class_remaining_seats,
                                                         'second_leg_economy_class_remaining_seats': second_leg_economy_class_remaining_seats})
