from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.postgres.fields import JSONField
from .auth_helper import get_client_token
from .graph_helper import MailGraph, get_user, send_invite_mail

# Create your models here.

class ClientUser(models.Model):
	email = models.EmailField()
	msid = models.CharField(max_length=512, null=True)
	token = JSONField()
	updated = models.DateTimeField(auto_now = True)
	created = models.DateTimeField(auto_now_add=True)
	

	def __str__(self):
		return self.email

	def get_token(self):
		return get_client_token(self)

	def get_name(self):
		user = get_user(self.get_token())
		if user['displayName']:
			return user['displayName']
		return '------'

	def get_mail(self, message_id):
		msg = MailGraph(self, get_token()).get_mail(message_id)
		return msg

	def get_mails(self):
		mg = MailGraph(self.get_token()).get_mails()
		return mg['value']

	def get_inbox(self):
		mg = MailGraph(self.get_token()).get_inbox()
		return mg['value']

	def get_sentitems(self):
		mg = MailGraph(self.get_token()).get_sentitems()
		return mg['value']

	def get_drafts(self):
		mg = MailGraph(self.get_token()).get_drafts()
		return mg['value']

	def get_deleteditems(self):
		mg = MailGraph(self.get_token()).get_deleteditems()
		return mg['value']

	def send_mail(self, to=[], subject=None, body=None, save_to_sent=False, cc=[]):
		mg = MailGraph(self.get_token()).send_mail(
			to=to,
			subject=subject,
			body=body)
		return mg

class InvitationMail(models.Model):
	display_name = models.CharField(max_length=60, null=True, blank=True)
	email = models.EmailField(unique = True)
	body = models.CharField(max_length=1000)
	redirect_url = models.URLField()
	reply_data = JSONField(null=True)
	sent = models.BooleanField(default=False, editable=False)

	def send_invitation(self):
		invitation_obj = send_invite_mail(
			display_name= self.display_name,
			email=self.email,
			body=self.body,
			invite_rdr_url=self.redirect_url)
		self.sent = invitation_obj["sendInvitationMessage"]
		self.save()
		return invitation_obj

def validate_excel_extension(value):
	if not value.name.endswith('.xls'):
		raise ValidationError(u'please provide an excel document with .xls extension')


class MassInvite(models.Model):
	file_upload = models.FileField(upload_to='mass_invite_files')

class InvitedUser(models.Model):
	state = models.CharField(max_length=1000, null=True)
	email = models.EmailField()
	login_url = models.URLField()