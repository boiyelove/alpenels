from django.db import models
# Create your models here.

class ClientUser(models.Model):
	email = models.EmailField(unique=True)
	msid = models.CharField(max_length=512, null=True)
	access_token = models.CharField(max_length= 1024, null=True)

	def __str__(self):
		return self.email
