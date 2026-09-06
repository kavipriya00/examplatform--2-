from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, Result


@login_required
def exam_list_view(request):
    exams = Exam.objects.filter(is_active=True)
    taken_ids = Result.objects.filter(student=request.user).values_list("exam_id", flat=True)
    return render(request, "exams/exam_list.html", {"exams": exams, "taken_ids": taken_ids})


@login_required
def take_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if Result.objects.filter(student=request.user, exam=exam).exists():
        return redirect("exam_list")

    if request.method == "POST":
        questions = exam.questions.all()
        score = 0
        for q in questions:
            selected = request.POST.get(f"question_{q.id}")
            if selected == q.correct_option:
                score += 1
        Result.objects.create(
            student=request.user, exam=exam, score=score, total_questions=questions.count()
        )
        return redirect("result_detail", exam_id=exam.id)

    questions = exam.questions.all()
    return render(request, "exams/take_exam.html", {"exam": exam, "questions": questions})
