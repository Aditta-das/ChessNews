from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Article

from django import forms
import re

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter password"
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if hasattr(self, "user_obj") and self.user_obj:
            return password
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Must contain uppercase letter.")

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Must contain lowercase letter.")

        if not re.search(r"[0-9]", password):
            raise forms.ValidationError("Must contain a number.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Must contain special character.")

        return password
    # otp = forms.CharField(required=False, max_length=6)


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




# Trials section for game upload form
from .models import UploadedGame, GameComment

class UploadedGameForm(forms.ModelForm):
    class Meta:
        model = UploadedGame
        fields = ['title', 'pgn']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Game title'
            }),
            'pgn': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control form-control-sm',
                'placeholder': 'Enter PGN with comments like {Your comment here}'
            }),
        }

class GameCommentForm(forms.ModelForm):
    class Meta:
        model = GameComment
        fields = ['move_number', 'comment']
        widgets = {
            'move_number': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Move number'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control form-control-sm',
                'placeholder': 'Enter your comment'
            }),
        }
