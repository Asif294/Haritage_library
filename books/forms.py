from typing import Any
from django import forms
from .models import Review,Borrow
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=['body','rating']