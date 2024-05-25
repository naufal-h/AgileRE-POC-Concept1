from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project
from django.utils.safestring import SafeString

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='')
    username = forms.CharField(max_length=150, help_text='')
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text=''  
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Minimum 8 characters'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Minimum 8 characters'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat your password', 'autocomplete': 'new-password'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 8:
            raise forms.ValidationError('Username must be at least 8 characters long.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password1

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['judul_project', 'deskripsi_project']
        
    def as_div(self):
        return SafeString(super().as_div().replace("<div>", "<div class='form-group'>")) 
