from django.contrib import admin

# Register your models here.

from .models import UserProfile
from .models import Flight


class FlightAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示 航班名称，出发地，目的地，起飞时间，到达时间，航线，价格，座位总数，订票总数
    list_display = ('flight_name', 'departure', 'destination', 'departure_time','arrival_time','airline',
                    'price','capacity','book_sum')

    # list_display_links = ('title', ) # 默认
    # sortable_by # 排序

    '''定义哪个字段可以编辑'''
    #list_editable = ('status',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    #list_max_show_all = 200  # default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['flight_name']

    '''按日期分组'''
    #date_hierarchy = 'create_date'

    '''默认空值'''
    empty_value_display = 'NA'

    '''过滤选项'''
    #list_filter = ('status', 'author__is_superuser',)

admin.site.register(Flight,FlightAdmin)