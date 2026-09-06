from django.db import models
from django.conf import settings
from academics.models import Subject


class Question(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]
    DIFFICULTY_CHOICES = [("BASIC", "Basic"), ("ADVANCED", "Advanced")]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    unit_number = models.PositiveIntegerField(default=1)
    topic_name = models.CharField(max_length=150, blank=True)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="BASIC")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_by_ai = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]


class Exam(models.Model):
    title = models.CharField(max_length=150)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    duration_minutes = models.PositiveIntegerField(default=30)
    questions = models.ManyToManyField(Question, related_name="exams", limit_choices_to={"status": "APPROVED"})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="results")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.score}/{self.total_questions}"
