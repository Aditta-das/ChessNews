from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Article

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


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['image', 'bio']  # Only the image field from UserProfile

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update User model fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        # Update profile image if uploaded
        image = self.cleaned_data.get('image')
        bio = self.cleaned_data.get('bio')
        profile.bio = bio   

        if image:
            profile.image = image

        if commit:
            user.save()
            profile.save()

        return profile


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'style': 'color: #f9f9f9; background-color: #373633; border: none !important;'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'd-none',  # hide default input
                'id': 'uploadBtn'   # give unique ID
            }),
        }
