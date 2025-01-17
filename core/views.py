import dateutil.parser
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormView, CreateView
from .auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from .graph_helper import get_user, get_calendar_events, get_contact_list, MailGraph
from .forms import ComposeMailForm, InvitationMailForm, MassInviteForm
from .models import ClientUser


class LoginRequiredMixin(LoginRequiredMixin):
  login_url = reverse_lazy('login')
  redirect_field_name = 'next'

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
  expected_state = request.session.pop('auth_state', '')
  token = get_token_from_code(request.get_full_path(), expected_state)

  user = get_user(token)
  store_token(request, token)
  store_user(request, user)
  usermail = user['mail'] if (user['mail'] != None) else user['userPrincipalName']
  try: 
    cuser = ClientUser.objects.get(email=usermail)
    cuser.token = token
    cuser.save()
  except:
    ClientUser.objects.create(email =  usermail,
      msid = user['id'],
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


class ClientList(LoginRequiredMixin, ListView):
  model = ClientUser
  template_name = 'alpenels/clientlist.html'
  context_object_name = 'client_list'

class ClientDetail(LoginRequiredMixin, DetailView):
  model = ClientUser

  def get_context_data(self, request, **kwargs):
    return context

class ClientInvitationCompose(LoginRequiredMixin, SuccessMessageMixin, CreateView):
  form_class = InvitationMailForm
  template_name = "alpenels/forms.html"
  success_message = "invitation Sent Successfully"
  success_url = reverse_lazy("compose-invitation")

  def form_valid(self, form):
    # form.cleaned_data.get('email')
    feedback  = form.done()
    print('feedback is', feedback)
    form.reply_data = feedback
    form.sent = feedback["sendInvitationMessage"]
    return super().form_valid(form)


# class ClientInvitationList(LoginRequiredMixin, View):
#   template_name = 'invitation_list.html'

class ClientMassInvite(LoginRequiredMixin, SuccessMessageMixin, CreateView):
  form_class = MassInviteForm
  template_name = "alpenels/mass_invite_form.html"
  success_message = 'File uplaoded successfull, invites will be sent'
  success_url = reverse_lazy('mass-invitation')

  # def form_valid(self, form):
  #   result = form.done()

















class ClientMailCompose(LoginRequiredMixin, SuccessMessageMixin, FormView):
  form_class = ComposeMailForm
  template_name = 'alpenels/forms.html'
  success_message = "Mail Sent Successfully!"

  def form_valid(self, form):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    msg = form.send_mail(cuser)
    if msg.status_code == 202:
      self.success_url = reverse_lazy('compose-mail', kwargs={'id': id})
      return super().form_valid(form)
    else:
      form.errors.update(msg.json())
      return super().form_invalid(form)

  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    context = super().get_context_data(**kwargs)
    context['description'] = "<strong>Author:</strong> %s <br>  <strong/>Email:</strong> %s " % (cuser.get_name(), cuser.email)
    context['client_id'] = cuser.id
    return context



class ClientMailList(LoginRequiredMixin, DetailView):
  model = ClientUser
  template_name = 'alpenels/mails.html'
  context_object_name = 'client'
  pk_url_kwarg = 'id'
  def get_context_data(self, *args, **kwargs):
    cuser = self.get_object()
    kwargs = super().get_context_data(**kwargs)
    kwargs['mail_list'] = cuser.get_mails()
    kwargs['client_id'] = cuser.id
    return kwargs


class ClientInbox(LoginRequiredMixin, TemplateView):
  template_name = 'alpenels/mails.html'
  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    kwargs['mail_list'] = cuser.get_inbox()
    kwargs['client_id'] = cuser.id
    return kwargs

class ClientDraft(LoginRequiredMixin, TemplateView):
  template_name = 'alpenels/mails.html'
  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    kwargs['mail_list'] = cuser.get_drafts()
    kwargs['client_id'] = cuser.id
    return kwargs

class ClientSentItems(LoginRequiredMixin, TemplateView):
  template_name = 'alpenels/mails.html'
  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    kwargs['mail_list'] = cuser.get_sentitems()
    kwargs['client_id'] = cuser.id
    return kwargs

class ClientDeletedItems(LoginRequiredMixin, TemplateView):
  template_name = 'alpenels/mails.html'
  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    cuser = get_object_or_404(ClientUser, pk=id)
    kwargs['mail_list'] = cuser.get_deleteditems()
    kwargs['client_id'] = cuser.id
    return kwargs

class ClientMail(LoginRequiredMixin, TemplateView):
  template_name = "alpenels/single_mail.html"

  def get_context_data(self, **kwargs):
    id  = self.kwargs.get('id')
    mid  = (self.kwargs.get('mid')).strip()
    print('mid is', mid)
    cuser = get_object_or_404(ClientUser, pk=id)
    mail = MailGraph(cuser.token).get_mail(mid)
    print('mail is', mail)
    kwargs['mail'] = mail
    kwargs['mail_body'] = mail['body']
    kwargs['client_id'] = id
    return kwargs

class ClientMailFolder(LoginRequiredMixin, TemplateView):
  def get_context_data(self, **kwargs):
    id  = self.request.kwargs.get('id')
    fid  = self.request.kwargs.get('fid')
    cuser = get_object_or_404(ClientUser, pk=id)
    kwargs['messages'] = MailGraph(cuser.token).get_folder_messages(id)

    return kwargs