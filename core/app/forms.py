from django import forms
from django.contrib.auth.forms import AuthenticationForm
from models.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Ваш email'})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Ваш пароль'}),
    )
    
    def clean_username(self):
        email = self.cleaned_data.get('username')
        validate_email(email)
        return email

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
    )

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'email']
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'patronymic': forms.TextInput(attrs={'placeholder': 'Отчество (необязательно)', 'required': False}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже существует")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        
        if len(password1) < 8:
            raise ValidationError("Пароль должен быть не менее 8 символов")
        
        if not re.search(r'[A-Z]', password1) or not re.search(r'[a-z]', password1) or not re.search(r'[0-9]', password1):
            raise ValidationError("Пароль должен содержать цифры, заглавные и строчные буквы")
            
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class VerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Код из письма', 'autofocus': True}),
        label="Код подтверждения"
    )