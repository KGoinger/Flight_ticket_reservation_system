from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import User  # 引入Django内置的User模型


# Create your models here.

class Flight(models.Model):
    # 利用django中默认自增的id作为主键
    flight_name = models.CharField(max_length=255)  # 班次，比如CZ8739，最大长度255。
    departure = models.CharField(max_length=255)  # 起飞地点
    destination = models.CharField(max_length=255)  # 目的地
    departure_time = models.DateTimeField()  # 起飞时间
    arrival_time = models.DateTimeField()  # 到达时间
    airline = models.CharField(max_length=255)  # 航空公司
    # price = models.DecimalField(max_digits=10, decimal_places=2)  # 票价
    # capacity = models.IntegerField(default=0, null=True)  # 座位总数
    # book_sum = models.IntegerField(default=0, null=True)  # 订票总人数
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2)  # 头等舱票价
    first_class_capacity = models.IntegerField(default=0, null=True)  # 头等舱座位总数
    first_class_book_sum = models.IntegerField(default=0, null=True)  # 头等舱订票总人数
    economy_class_price = models.DecimalField(max_digits=10, decimal_places=2)  # 经济舱票价
    economy_class_capacity = models.IntegerField(default=0, null=True)  # 经济舱座位总数
    economy_class_book_sum = models.IntegerField(default=0, null=True)  # 经济舱订票总人数
    seat_info = models.TextField()  # 用TextField处理长文本字段
    duration = models.CharField(max_length=10, blank=True)  # 添加持久化字段

    def save(self, *args, **kwargs):
        time_diff = self.arrival_time - self.departure_time  # 计算时间差
        hours, remainder = divmod(time_diff.total_seconds(), 3600)  # 将秒数转换为小时和余下的秒数
        minutes = remainder // 60  # 计算分钟
        self.duration = f'{int(hours)}h-{int(minutes)}m'  # 格式化时间差并赋值给duration字段
        super().save(*args, **kwargs)

    def get_price_by_class(self, class_type):
        if class_type == 'economy_class':
            return self.economy_class_price
        elif class_type == 'first_class':
            return self.first_class_price
        # 添加其他舱位类型的条件
        else:
            return 0  # 默认返回0或其他你认为合适的值
    def __str__(self):
        return self.flight_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.IntegerField()  # 用户余额
    resident_num = models.CharField('resident identity card number', max_length=18)  # 身份证号
    telephone = models.CharField('Telephone', max_length=11, blank=True)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    # 订单状态的选项
    ORDER_STATUS_CHOICES = [
        ('成功', '成功'),
        ('退票', '退票'),
    ]
    CLASS_TYPE_CHOICES = [
        ('first_class', '头等舱'),
        ('economy_class', '经济舱'),
    ]
    # Django会自动为您创建一个名为id的自增主键字段
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 直接使用User模型
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)  # 航班id
    class_type = models.CharField(max_length=50)  # 舱位类型
    booking_time = models.DateTimeField()  # 订票时间
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES)  # 订单状态
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 订单价格
    def __str__(self):
        return f"Order {self.id}"  # 使用默认的id字段


class FinancialReport(models.Model):
    report_id = models.AutoField(primary_key=True)  # 报告的唯一id
    creation_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)  # 总收入
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2)  # 总支出
    profit = models.DecimalField(max_digits=10, decimal_places=2)  # 利润

    def __str__(self):
        return f"Financial Report {self.report_id}"
