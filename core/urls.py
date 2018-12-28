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
  path('client-list/', views.ClientList.as_view(), name='clientlist'),
  path('client-list/<int:id>/', views.ClientDetail.as_view, name='client-detail'),
  path('client-list/<int:id>/compose/', views.ClientMailCompose.as_view, name='compose-mail'),
  path('client-list/<int:id>/mails/', views.ClientMailList.as_view(), name='list-mail'),
  path('client-list/<int:id>/<int:fid>/', views.ClientMailFolder.as_view(), name='list-mail-folder'),
]	