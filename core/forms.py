from django import forms
from django.core.validators import validate_email
from .models import InvitationMail, MassInvite
from .graph_helper import send_invite_mail

class InvitationMailForm(forms.ModelForm):
	display_name = forms.CharField(max_length=50, required=False)
	email = forms.EmailField()
	body = forms.CharField(widget=forms.Textarea)
	redirect_url = forms.URLField()

	class Meta:
		model = InvitationMail
		exclude  = ('reply_data','sent')

	def clean_email(self):
		email = self.cleaned_data.get('email')
		exists = InvitationMail.objects.filter(email=email)
		if exists:
			raise forms.ValidationError('An invitation has already been sent to this email address')
		return email


	def done(self):
		invitation_obj = send_invite_mail(
			display_name= self.cleaned_data.get('display_name'),
			email=self.cleaned_data.get('email'),
			body=self.cleaned_data.get('body'),
			invite_rdr_url=self.cleaned_data.get('redirect_url'))
		return invitation_obj


class ComposeMailForm(forms.Form):
	recipient = forms.CharField(max_length=512)
	subject = forms.CharField(max_length=100)
	body = forms.CharField(widget=forms.Textarea)
	save_to_sent_items = forms.BooleanField(required=False, initial=True)

	def clean_recipient(self):
		rc = self.cleaned_data.get('recipient')
		rc_list =  rc.split(',')
		rc_list0 = []
		for rc0 in rc_list:
			rc0 = rc0.strip()
			try:
				validate_email(rc0)
				rc_list0.append(rc0)
			except:
				raise forms.ValidationError('{} is not a valid email address'.format(rc0))
		return rc

	def done(self, mgraph):
		pass

	def get_email_list(self):
		rc = self.cleaned_data.get('recipient')
		rc_list =  rc.split(',')
		rc_list0 = []
		for rc0 in rc_list:
			rc0 = rc0.strip()
			rc_list0.append(rc0)
		return rc_list0

	def send_mail(self, cuser):
		return cuser.send_mail(
			to = self.get_email_list(),
			subject = self.cleaned_data.get('subject'),
			body = self.cleaned_data.get('body'),
			save_to_sent = self.cleaned_data.get('save_to_sent_items')
			)

class MassInviteForm(forms.ModelForm):
	file_upload = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/vnd.ms-excel'}))

	class Meta:
		model = MassInvite
		fields = '__all__'