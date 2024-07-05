from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .constants import GENDER_TYPE
from  django.contrib.auth.models import User
from .models import UserLibraryAccount,UserAddress,Deposite
class UserRegistrationFrom(UserCreationForm):
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    phone_number=forms.CharField(max_length=11)
    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)

    class Meta:
        model=User
        fields=['username','password1','password2','first_name','last_name','email','phone_number'
                ,'birth_date','gender','postal_code','city','country','street_address']
        
    def save(self, commit=True):
        our_user=super().save(commit=False)
        if commit ==True:
            our_user.save()
            phone_number=self.cleaned_data.get('phone_number')
            gender=self.cleaned_data.get('gender')
            postal_code=self.cleaned_data.get('postal_code')
            country=self.cleaned_data.get('country')
            birth_date=self.cleaned_data.get('birth_date')
            city=self.cleaned_data.get('city')
            street_address=self.cleaned_data.get('street_address')
             
            UserAddress.objects.create(
                user=our_user,
                postal_code=postal_code,
                country=country,
                street_address=street_address,
                city=city

             )
            UserLibraryAccount.objects.create(
                user=our_user,
                phone_number=phone_number,
                gender= gender,
                birth_date=birth_date,
                account_no=100000+our_user.id
            )
        return our_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                ) 
            })

class UserUpdateForm(forms.ModelForm):
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    phone_number=forms.CharField(max_length=11)
    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        if self.instance:
            try:    
                user_account = self.instance.account
                user_address = self.instance.address
            except UserLibraryAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['phone_number'].initial = user_account.phone_number
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_account, created = UserLibraryAccount.objects.get_or_create(user=user) 
            user_address, created = UserAddress.objects.get_or_create(user=user) 
            user_account.phone_number = self.cleaned_data['phone_number']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()
            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user       

class DepositeForm(forms.ModelForm):
    class Meta:
        model = Deposite
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.account:
            instance.account = self.account
        if commit:
            instance.save()
        return instance
    
class ProfileUpdateForm(forms.ModelForm):
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)

    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        if self.instance:
            try:    
                user_account = self.instance.account
                user_address = self.instance.address
            except UserRegistrationFrom.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
            
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserRegistrationFrom.objects.get_or_create(user=user) # jodi account thake taile seta jabe user_account ar jodi account na thake taile create hobe ar seta created er moddhe jabe
            user_address, created = UserAddress.objects.get_or_create(user=user) 

          
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user       
   