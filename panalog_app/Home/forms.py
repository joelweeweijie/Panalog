from django import forms
from .models import Ticket
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class detailsform(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = "__all__"

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ticketform(ModelForm):

    class Meta:
        model = Ticket
        fields = ('ticketNo', 'customercode', 'date_created')




