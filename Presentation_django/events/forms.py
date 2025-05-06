from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, Category, Tag
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'image', 'category', 'tags']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple(),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class RegistrationForm(forms.Form):
    name = forms.CharField(label="Full Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        help_text="Must be at least 8 characters, contain a number, and upper, lower, and special characters.",
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        help_text="Enter your password again.",
    )
    mobile = forms.CharField(
        label="Mobile Number",
        max_length=10,  
        min_length=10,  
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[RegexValidator(r'^[0-9]{10}$', message="Enter a valid 10-digit mobile number.", code='invalid_mobile')],
        help_text="Enter your 10-digit mobile number.",
    )
    role = forms.CharField(widget=forms.HiddenInput)  

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password) 
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):  
    email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-input'}))