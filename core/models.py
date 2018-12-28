from django.db import models
from auth_helper import get_client_token
# Create your models here.

class ClientUser(models.Model):
	email = models.EmailField(unique=True)
	msid = models.CharField(max_length=512, null=True)
	access_token = models.CharField(max_length= 1024, null=True)
	expires_at = models.DateTimeField(null=True)

	def __str__(self):
		return self.email

	def get_token(self):
		return get_client_token(self.access_token)
