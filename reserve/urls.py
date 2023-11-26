from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('logout/', views.logout, name='logout'),
]