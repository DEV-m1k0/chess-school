from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email

class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        # Генерируем username на основе email
        username = email.split('@')[0]
        # Убедимся, что username уникален
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{email.split('@')[0]}_{counter}"
            counter += 1
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Ученик'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Админ'),
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,  # Разрешаем не уникальные значения
        blank=True,    # Разрешаем пустое значение
        null=True,     # Разрешаем NULL
        help_text=_('Не обязательно. 150 символов или меньше.'),
    )
    last_name = models.CharField(_('last name'), max_length=150)
    first_name = models.CharField(_('first name'), max_length=150)
    patronymic = models.CharField(_('patronymic'), max_length=150, blank=True)  # Отчество (необязательное)
    
    email = models.EmailField(
        _('email address'), 
        unique=True,
        validators=[validate_email],
        error_messages={
            'unique': _("Пользователь с такой почтой уже существует."),
        }
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_groups')
    students = models.ManyToManyField(User, related_name='study_groups')
    created_at = models.DateTimeField(default=timezone.now)
