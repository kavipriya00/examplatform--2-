import pdfplumber
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from exams.models import Question
from .forms import SyllabusUploadForm
from .models import Syllabus
from . import ai_helper


@login_required
def upload_syllabus_view(request):
    if request.method == "POST":
        form = SyllabusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            syllabus = form.save()

            # Extract text from the uploaded PDF (Module 3: AI Syllabus Analyzer)
            text_parts = []
            with pdfplumber.open(syllabus.pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            syllabus.extracted_text = "\n".join(text_parts)
            syllabus.save()

            messages.success(request, "Syllabus uploaded and text extracted.")
            return redirect("generate_questions", syllabus_id=syllabus.id)
    else:
        form = SyllabusUploadForm()
    return render(request, "syllabus_ai/upload.html", {"form": form})


@login_required
def generate_questions_view(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)

    if request.method == "POST":
        unit_number = int(request.POST.get("unit_number", 1))
        difficulty = request.POST.get("difficulty", "BASIC")
        count = int(request.POST.get("count", 5))

        generated = ai_helper.generate_questions(
            syllabus_text=syllabus.extracted_text,
            unit_number=unit_number,
            difficulty=difficulty,
            count=count,
        )

        if not generated:
            messages.error(request, "AI did not return usable questions. Try again.")
        else:
            for q in generated:
                Question.objects.create(
                    subject=syllabus.subject,
                    unit_number=unit_number,
                    topic_name=q.get("topic_name", ""),
                    text=q.get("question", ""),
                    option_a=q.get("option_a", ""),
                    option_b=q.get("option_b", ""),
                    option_c=q.get("option_c", ""),
                    option_d=q.get("option_d", ""),
                    correct_option=q.get("correct_option", "A"),
                    explanation=q.get("explanation", ""),
                    difficulty=difficulty,
                    status="PENDING",
                    created_by_ai=True,
                )
            messages.success(request, f"{len(generated)} questions generated. Review them below.")
        return redirect("review_questions", syllabus_id=syllabus.id)

    return render(request, "syllabus_ai/generate.html", {"syllabus": syllabus})


@login_required
def review_questions_view(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    pending = Question.objects.filter(subject=syllabus.subject, status="PENDING")
    return render(request, "syllabus_ai/review.html", {"syllabus": syllabus, "questions": pending})


@login_required
def approve_question_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.status = "APPROVED"
    question.save()
    return redirect("review_questions", syllabus_id=question.subject.syllabi.first().id)


@login_required
def reject_question_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    syllabus_id = question.subject.syllabi.first().id
    question.delete()
    return redirect("review_questions", syllabus_id=syllabus_id)
