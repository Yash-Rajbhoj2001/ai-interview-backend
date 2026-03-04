from django.db import models
from django.conf import settings

class JobDescription(models.Model):

    ROLE_CHOICES = [
        ("BACKEND", "Backend Developer"),
        ("FRONTEND", "Frontend Developer"),
        ("FULLSTACK", "Fullstack Developer"),
        ("DATA", "Data Scientist"),
        ("DEVOPS", "DevOps Engineer"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="OTHER"
    )

    title = models.CharField(max_length=255)

    company_name = models.CharField(max_length=255, null=True, blank=True)

    original_text = models.TextField()

    parsed_data = models.JSONField(default=dict)

    expires_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title