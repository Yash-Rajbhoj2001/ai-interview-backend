from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # remove username completely

    email = models.EmailField(unique=True)

    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('SINGLE', 'Single'),
        ('PRO', 'Pro'),
        ('PREMIUM', 'Premium'),
    ]

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='FREE'
    )

    interviews_remaining = models.IntegerField(default=1)

    billing_cycle = models.CharField(
        max_length=10,
        choices=[('MONTHLY', 'Monthly'), ('YEARLY', 'Yearly')],
        default='MONTHLY'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email