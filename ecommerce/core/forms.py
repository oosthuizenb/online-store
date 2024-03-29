from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, ReadOnlyPasswordHashField, UserCreationForm, UserChangeForm

from .models import Address, Review

User = get_user_model()

class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password_confirm'].widget.attrs.update({'placeholder': 'Confirm password'})
        
    # Validate that the username is unique
    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.filter(email=data)
        if qs.exists():
            raise ValidationError("The username already exists.")
        return data
    
    def clean_password(self):
        data = self.cleaned_data['password']
        # This raises a ValidationError if it's invalid
        validate_password(data)
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

class CustomUserCreationForm(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]

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
    
    def clean_zip_code(self):
        data = self.cleaned_data['zip_code']
        if not data.isdigit():
            raise ValidationError('Zip code can only contain digits.')
        return data
    
    def clean_mobile_number(self):
        data = self.cleaned_data['mobile_number']
        # Mobile number can only contain digits
        if not data.isdigit():
            raise ValidationError('Mobile number can only contain digits.')
        # Mobile number must have a length of 10 characters
        if not len(data) == 10:
            raise ValidationError('Mobile number must contain 10 digits.')
        return data
    
    class Meta:
        model = Address
        exclude = ['user']
        

class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'min': 1, 'max': 5, 'value': 5})

    def clean_rating(self):
        data = self.cleaned_data['rating']
        if data < 1 or data > 5:
            raise ValidationError('Rating must be in the range from 1 to 5.')
        return data

    class Meta:
        model = Review
        exclude = ['user', 'product', 'publish_date']



        
# TODO create payment form and maybe order form?

