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

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Call(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    meeting_url = models.URLField()

class Assignment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

class Material(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='materials/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class ChessGame(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games')
    pgn = models.TextField()
    played_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_reviews')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class JobApplication(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    message = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено')
    ), default='pending')

class LessonBooking(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_lessons')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)