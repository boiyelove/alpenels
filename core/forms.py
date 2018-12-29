from django import forms
from django.core.validators import validate_email

class InvitationMail(forms.Form):
	email = forms.EmailField()
	body = forms.CharField(widget=forms.Textarea)
	cc = forms.CharField(max_length=512)
	def clean_cc(self):
		cc = self.cleaned_data.get('cc')
		cc_split = cc.split(',')
		for c in cc_split:
			if '@' not in c:raise Forms.ValidationError('Enter valid cc mails')
		return cc


class ComposeMailForm(forms.Form):
	recipient = forms.CharField(max_length=512)
	subject = forms.CharField(max_length=100)
	body = forms.CharField(widget=forms.Textarea)
	save_to_sent_items = forms.BooleanField(required=False)

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
			body = self.cleaned_data.get('body')
			)
