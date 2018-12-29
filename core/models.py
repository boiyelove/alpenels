from django.db import models
from django.contrib.postgres.fields import JSONField
from .auth_helper import get_client_token
from .graph_helper import MailGraph

# Create your models here.

class ClientUser(models.Model):
	email = models.EmailField(unique=True)
	msid = models.CharField(max_length=512, null=True)
	token = JSONField()
	access_token = models.CharField(max_length= 2048, null=True)
	access_token_exp = models.PositiveIntegerField(default=3599)
	refresh_token = models.CharField(max_length= 2048, null=True)
	updated = models.DateTimeField(auto_now = True)
	created = models.DateTimeField(auto_now_add=True)
	

	def __str__(self):
		return self.email

	def get_token(self):
		return get_client_token(self)


	def get_mails(self):
		mg = MailGraph(self.get_token()).get_mails()
		return mg['value']

	def get_inbox(self):
		mg = MailGraph(self.get_token()).get_inbox()
		return mg['value']

	def send_mail(self, to=[], subject=None, body=None, save_to_sent=False, cc=[]):
		mg = MailGraph(self.get_token()).send_mail(
			to=to,
			subject=subject,
			body=body)
		return mg
