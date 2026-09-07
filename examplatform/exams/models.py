from django.db import models
from django.conf import settings
from academics.models import Subject


class Question(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]
    DIFFICULTY_CHOICES = [("BASIC", "Basic"), ("ADVANCED", "Advanced")]
    TYPE_CHOICES = [("MCQ", "Multiple Choice"), ("LONG", "Long Answer")]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    unit_number = models.PositiveIntegerField(default=1)
    topic_name = models.CharField(max_length=150, blank=True)
    question_type = models.CharField(max_length=4, choices=TYPE_CHOICES, default="MCQ")
    marks = models.PositiveIntegerField(default=1)
    text = models.TextField()
    # MCQ-only fields — left blank for LONG questions
    option_a = models.CharField(max_length=255, blank=True)
    option_b = models.CharField(max_length=255, blank=True)
    option_c = models.CharField(max_length=255, blank=True)
    option_d = models.CharField(max_length=255, blank=True)
    correct_option = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")], blank=True)
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="BASIC")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_by_ai = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.marks}m] {self.text[:50]}"


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
    total_marks = models.PositiveIntegerField(default=0)
    obtained_marks = models.PositiveIntegerField(default=0)
    fully_graded = models.BooleanField(default=False)  # False while long-answers await manual grading
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.obtained_marks}/{self.total_marks}"


class Answer(models.Model):
    """One student's answer to one question within one exam attempt."""
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)  # for MCQ
    text_answer = models.TextField(blank=True)  # for LONG
    marks_awarded = models.PositiveIntegerField(null=True, blank=True)  # null = not graded yet
    graded_by_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to Q{self.question_id} in Result {self.result_id}"