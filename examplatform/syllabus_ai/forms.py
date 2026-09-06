from django import forms
from .models import Syllabus


class SyllabusUploadForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = ["subject", "pdf_file"]
