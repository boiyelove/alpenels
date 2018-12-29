import dateutil.parser
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from .auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from .graph_helper import get_user, get_calendar_events, get_contact_list, MailGraph
from .forms import ComposeMailForm
from .models import ClientUser


def home(request):
  context = initialize_context(request)

  return render(request, 'alpenels/home.html', context)

def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  # context['user'] = request.session.get('user', {'is_authenticated': False})
  return context

def sign_in(request):
  # Get the sign-in URL
  sign_in_url, state = get_sign_in_url()
  # Save the expected state so we can validate in the callback
  request.session['auth_state'] = state
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(sign_in_url)

def callback(request):
  # Get the state saved in session
  expected_state = request.session.pop('auth_state', '')

  # Make the token request
  token = get_token_from_code(request.get_full_path(), expected_state)
  print('this token here is', token)

  # Get the user's profile
  user = get_user(token)
  store_token(request, token)
  store_user(request, user)
  usermail = user['mail'] if (user['mail'] != None) else user['userPrincipalName']
  try: 
    cuser = ClientUser.objects.get(email=usermail)
    cuser.access_token = token['access_token'],
    refresh_token=token['refresh_token']
    cuser.token = token
    cuser.save()
  except:
    ClientUser.objects.create(email =  usermail,
      msid = user['id'],
      access_token=token['access_token'],
      refresh_token=token['refresh_token'],
      token = token) 
  return HttpResponseRedirect('https://outlook.office.com/owa/')

def sign_out(request):
  remove_user_and_token(request)
  return HttpResponseRedirect(reverse('home'))

def calendar(request):
  context = initialize_context(request)
  token = get_token(request)
  events = get_calendar_events(token)

  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
    for event in events['value']:
      event['start']['dateTime'] = dateutil.parser.parse(event['start']['dateTime'])
      event['end']['dateTime'] = dateutil.parser.parse(event['end']['dateTime'])

    context['events'] = events['value']

  return render(request, 'alpenels/calendar.html', context)

def contact(request):
  context = initialize_context(request)
  token = get_token(request)
  contact_list = get_contact_list(token)
  context['contact_list'] = contact_list
  return render(request, 'alpenels/contactlist.html', context)

def mail(request):
  context = initialize_context(request)
  token = get_token(request)
  mail_list = MailGraph(token).get_mails()
  context['mail_list'] = mail_list['value']
  return render(request, 'alpenels/mails.html', context)

def accountlist(request):
  context = initialize_context(request)
  # token = get_token(request)
  context['accountlist'] = ClientUser.objects.all()
  return render(request, "alpenels/accountlist.html", context)

def accountdetail(request):
  context = initialize_context(request)
  return render(request, "alpenels/accountdetail.html", context)

def invitations(request):
  context = initialize_context(request)
  return render(request, "alpenels/invitations.html", context)


class ClientList(ListView):
  model = ClientUser
  template_name = 'alpenels/clientlist.html'
  context_object_name = 'client_list'

class ClientDetail(DetailView):
  model = ClientUser

  def get_context_data(self, request, **kwargs):
    return context

class ClientMailCompose(FormView):
  form_class = ComposeMailForm
  template_name = 'alpenels/forms.html'

  def form_valid(self, form):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    msg = form.send_mail(cuser)
    print('msg is', msg)
    print('msg json is', msg)
    # mg = 
    self.success_url = reverse_lazy('compose-mail', kwargs={'id': id})
    return super().form_valid(form)

class ClientMailList(DetailView):
  model = ClientUser
  template_name = 'alpenels/mails.html'
  context_object_name = 'client'
  pk_url_kwarg = 'id'
  def get_context_data(self, *args, **kwargs):
    cuser = self.get_object()
    kwargs = super().get_context_data(**kwargs)
    kwargs['mail_list'] = cuser.get_mails()
    return kwargs




class ClientMailFolder(TemplateView):
  def get_context_data(self, **kwargs):
    id  = self.request.kwargs.get('id')
    fid  = self.request.kwargs.get('fid')
    cuser = get_object_or_404(ClientUser, id)
    kwargs['messages'] = MailGraph(cuser.access_token).get_folder_messages(id)

    return kwargs