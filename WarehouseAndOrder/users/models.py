from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"