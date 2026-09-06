from django.db import models
from academics.models import Subject


class Syllabus(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="syllabi")
    pdf_file = models.FileField(upload_to="syllabus_pdfs/")
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Syllabus for {self.subject.name}"
