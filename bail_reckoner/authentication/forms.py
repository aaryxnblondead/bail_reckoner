from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        
        return cleaned_data

class UserLoginForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class AadhaarVerificationForm(forms.Form):
    """Form for Aadhaar verification"""
    aadhaar_number = forms.CharField(max_length=12, min_length=12)
    otp = forms.CharField(max_length=6, min_length=6)