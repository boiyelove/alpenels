from django.urls import path, re_path

from . import views

urlpatterns = [
  # /
  path('', views.home, name='home'),
  path('signin', views.sign_in, name='signin'),
  path('callback', views.callback, name='callback'),
  path('signout', views.sign_out, name='signout'),
  path('calendar', views.calendar, name='calendar'),
  path('contact/', views.contact, name='contact'),
  path('clients/', views.ClientList.as_view(), name='list-client'),
  path('client/<int:id>/', views.ClientDetail.as_view, name='client-detail'),
  path('client/<int:id>/compose/', views.ClientMailCompose.as_view(extra_context={'form_title':'Compose Mail'}), name='compose-mail'),
  path('client/<int:id>/mails/', views.ClientMailList.as_view(), name='list-mail'),
  path('client/<int:id>/inbox/', views.ClientInbox.as_view(), name='client-inbox'),
  re_path(r'^client/(?P<id>\d+)/inbox/(?P<mid>.+)/$', views.ClientMail.as_view(), name='client-mail'),
  path('client/<int:id>/sentitems/', views.ClientSentItems.as_view(), name='client-sentitems'),
  path('client/<int:id>/drafts/', views.ClientDraft.as_view(), name='client-drafts'),
  path('client/<int:id>/trash/', views.ClientDeletedItems.as_view(), name='client-trash'),
  path('client/<int:id>/<int:fid>/', views.ClientMailFolder.as_view(), name='list-mail-folder'),

]	