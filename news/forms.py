from django import forms
from django.contrib.auth.models import User

class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(required=False, max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    otp = forms.CharField(required=False, max_length=6)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username
