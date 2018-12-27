from django.urls import path

from . import views

urlpatterns = [
  # /
  path('', views.home, name='home'),
  path('signin', views.sign_in, name='signin'),
  path('callback', views.callback, name='callback'),
  path('signout', views.sign_out, name='signout'),
  path('calendar', views.calendar, name='calendar'),
  path('contact/', views.contact, name='contact'),
  path('mail/', views.mail, name='mail'),
  path('accountlist/', views.accountlist, name='accountlist'),
  path('accountdetail/', views.accountdetail, name='accountdetail' )
]