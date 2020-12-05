from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Address

class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
        
# Custom place holder text for Login widgets
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})

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
        