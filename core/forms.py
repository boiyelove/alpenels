from django import forms

class InvitationMail(forms.Form):
	email = models.EmailField()
	body = models.TextField()
	cc = models.CharField(max_length=512)
	def clean_cc(self):
		cc = self.cleaned_data.get('cc')
		cc_split = cc.split(',')
		for c in cc_split:
			if '@' not in c:raise Forms.ValidationError('Enter valid cc mails')
		return cc