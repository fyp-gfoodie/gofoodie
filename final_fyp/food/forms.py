from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'



