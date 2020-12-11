from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Address

class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    password_confirm = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password_confirm'].widget.attrs.update({'placeholder': 'Confirm password'})
        
    # Validate that the username is unique
    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.filter(username=data)
        if qs.exists():
            raise ValidationError("The username already exists.")
        return data
    
    # Validate that the passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise ValidationError('Passwords must match.')
        
# Custom place holder text for Login widgets
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})

# Place holder text for address form widgets
class AddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Recipient Name'})
        self.fields['zip_code'].widget.attrs.update({'placeholder': 'Zip Code'})    
        self.fields['city'].widget.attrs.update({'placeholder': 'City/Town'})    
        self.fields['suburb'].widget.attrs.update({'placeholder': 'Suburb'})    
        self.fields['street_address'].widget.attrs.update({'placeholder': 'Street Address'})    
        self.fields['mobile_number'].widget.attrs.update({'placeholder': 'Mobile Number'})    
        
    class Meta:
        model = Address
        exclude = ['user']
        