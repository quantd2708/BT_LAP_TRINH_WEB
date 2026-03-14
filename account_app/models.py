# account_app/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Khai báo các lựa chọn cho quyền (role)
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    # Thêm các trường theo đúng thiết kế SQL ban đầu của Quân
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # Django AbstractUser đã có sẵn: username, password, email, is_active, is_staff...
    def __str__(self):
        return self.username