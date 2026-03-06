from django.db import models
from django.conf import settings
from apps.job_descriptions.models import JobDescription

# INTERVIEW SESSION MODEL
class InterviewSession(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    INTERVIEW_TYPES = [
        ("HR", "HR"),
        ("Technical", "Technical"),
        ("Mixed", "Mixed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    jd = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE
    )

    interview_type = models.CharField(
        max_length=20,
        choices=INTERVIEW_TYPES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    # started_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    ended_at = models.DateTimeField(null=True, blank=True)

    duration_seconds = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


# TRANSCRIPT MESSAGE MODEL
class TranscriptMessage(models.Model):

    SPEAKER_CHOICES = [
        ("AI", "AI"),
        ("Candidate", "Candidate"),
    ]

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE
    )

    speaker = models.CharField(
        max_length=20,
        choices=SPEAKER_CHOICES
    )

    message_text = models.TextField()

    message_order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


# TOKEN USAGE MODEL
class TokenUsage(models.Model):

    session = models.OneToOneField(
        InterviewSession,
        on_delete=models.CASCADE
    )

    input_token = models.IntegerField()

    output_token = models.IntegerField()

    total_token = models.IntegerField()

    cost_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=4
    )

    created_at = models.DateTimeField(auto_now_add=True)


# SCORES MODEL
class Score(models.Model):

    session = models.OneToOneField(
        InterviewSession,
        on_delete=models.CASCADE
    )

    technical_score = models.DecimalField(max_digits=5, decimal_places=2)

    communication_score = models.DecimalField(max_digits=5, decimal_places=2)

    relevance_score = models.DecimalField(max_digits=5, decimal_places=2)

    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)

    problem_solving_score = models.DecimalField(max_digits=5, decimal_places=2)

    ai_score = models.DecimalField(max_digits=5, decimal_places=2)

    rule_score = models.DecimalField(max_digits=5, decimal_places=2)

    final_score = models.DecimalField(max_digits=5, decimal_places=2)

    feedback = models.TextField()

    scoring_version = models.CharField(
        max_length=10,
        default="v1.0"
    )

    created_at = models.DateTimeField(auto_now_add=True)


# INTERVIEW QUESTION MODEL
class InterviewQuestion(models.Model):

    interview = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=50,
        default="technical"
    )

    difficulty = models.CharField(
        max_length=20,
        default="medium"
    )

    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question {self.order} - {self.interview.id}"
    

# INTERVIEW ANSWER MODEL
class InterviewAnswer(models.Model):

    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    answer_text = models.TextField()

    ai_score = models.FloatField(null=True, blank=True)

    feedback = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for Question {self.question.id}"
    

# INTERVIEW REPORT MODEL
class InterviewReport(models.Model):

    interview = models.OneToOneField(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="report"
    )

    overall_score = models.FloatField(null=True, blank=True)

    technical_score = models.FloatField(null=True, blank=True)

    communication_score = models.FloatField(null=True, blank=True)

    strengths = models.TextField()

    weaknesses = models.TextField()

    suggestions = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Interview {self.interview.id}"