from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm, RegistrationForm, VerificationForm
from models.models import User
import random
from django.utils import timezone
from datetime import timedelta
import logging
from django.core.mail import EmailMessage
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import logout
from django.urls import reverse_lazy
logger = logging.getLogger(__name__)

class AuthView(View):
    template_name = 'churki.html'
    
    def get(self, request):
        
        if 'logout' in request.GET:
            logout(request)
            messages.info(request, 'Вы успешно вышли из системы')
            return redirect('index')
        
        if request.user.is_authenticated:
            return redirect('index')

            
        context = {
            'login_form': LoginForm(prefix='login'),
            'reg_form': RegistrationForm(prefix='register'),
            'verify_form': VerificationForm(prefix='verify'),
            'show_verification': 'verify_email' in request.session
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Обработка формы входа
        if 'login_submit' in request.POST:
            return self.handle_login(request)
        
        # Обработка формы регистрации
        elif 'register_submit' in request.POST:
            return self.handle_registration(request)
        
        # Обработка подтверждения email
        elif 'verify_submit' in request.POST:
            return self.handle_verification(request)
        
        return self.get(request)
    
    def handle_login(self, request):
        login_form = LoginForm(request, data=request.POST, prefix='login')
        if login_form.is_valid():
            email = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'Подтвердите email для входа')
            else:
                messages.error(request, 'Неверный email или пароль')
        
        context = self.get_context_data(login_form=login_form)
        return render(request, self.template_name, context)
    
    def handle_registration(self, request):
        reg_form = RegistrationForm(request.POST, prefix='register')
        if reg_form.is_valid():
            user = reg_form.save(commit=False)
            user.is_email_verified = False
            
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.email_verification_token = verification_code
            user.token_created_at = timezone.now()
            user.save()
            
            try:
                # Отправка письма с явным указанием кодировки
                email = EmailMessage(
                    'Подтверждение регистрации',
                    f'Ваш код подтверждения: {verification_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email.encoding = 'utf-8'  # Критически важная строка
                email.send(fail_silently=False)
            except Exception as e:
                logger.error(f"Ошибка отправки письма: {e}")
                messages.error(request, 'Ошибка отправки письма. Попробуйте позже.')
                return redirect('auth_page')
            
            request.session['verify_email'] = user.email
            messages.success(request, 'Код подтверждения отправлен на вашу почту')
            return redirect('auth_page')
        
        context = self.get_context_data(reg_form=reg_form)
        return render(request, self.template_name, context)
    
    def handle_verification(self, request):
        verify_form = VerificationForm(request.POST, prefix='verify')
        if verify_form.is_valid():
            email = request.session.get('verify_email')
            code = verify_form.cleaned_data.get('code')
            
            if email:
                try:
                    user = User.objects.get(email=email)
                    # Проверка кода и времени (10 минут)
                    if (user.email_verification_token == code and 
                        timezone.now() < user.token_created_at + timedelta(minutes=10)):
                        user.is_email_verified = True
                        user.save()
                        del request.session['verify_email']
                        messages.success(request, 'Email успешно подтвержден! Теперь войдите')
                        return redirect('auth_page')
                    else:
                        messages.error(request, 'Неверный или устаревший код')
                except User.DoesNotExist:
                    messages.error(request, 'Ошибка подтверждения')
            else:
                messages.error(request, 'Сессия истекла')
        
        context = self.get_context_data(verify_form=verify_form, show_verification=True)
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = {
            'login_form': kwargs.get('login_form', LoginForm(prefix='login')),
            'reg_form': kwargs.get('reg_form', RegistrationForm(prefix='register')),
            'verify_form': kwargs.get('verify_form', VerificationForm(prefix='verify')),
            'show_verification': kwargs.get('show_verification', False)
        }
        return context

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset/password_reset.html'
    email_template_name = 'password_reset/email/password_reset_email.html'
    subject_template_name = 'password_reset/email/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        # Проверка существования email
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'Пользователь с таким email не найден')
            return self.form_invalid(form)
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset/password_reset_complete.html'