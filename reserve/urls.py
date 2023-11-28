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
]