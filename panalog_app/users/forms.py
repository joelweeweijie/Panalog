from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    fullname = forms.CharField(max_length=50, help_text="**The names must match to assigned in ITMAS (Last, First) e.g. Wee, Joel / Kurniawan, Dhany / Jadhav, Sumit ")

    class Meta:
        model = User
        fields = ['username', 'fullname' ,'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["username"].widget.attrs["readonly"] = True

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'team']