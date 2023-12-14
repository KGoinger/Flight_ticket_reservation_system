from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('logout/', views.logout, name='logout'),
    path('finance/', views.finance, name='finance'),
    path('book_ticket/<int:flight_id>/', views.book_ticket, name='book_ticket'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('recharge/', views.recharge, name='recharge'),
    path('book_transfer/<int:first_leg_id>/<int:second_leg_id>/', views.book_transfer_ticket, name='book_transfer_ticket'),
]