from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, Result, Answer


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

    questions = exam.questions.all()

    if request.method == "POST":
        total_marks = sum(q.marks for q in questions)
        obtained_marks = 0
        all_graded = True

        result = Result.objects.create(
            student=request.user, exam=exam, total_marks=total_marks, obtained_marks=0
        )

        for q in questions:
            if q.question_type == "MCQ":
                selected = request.POST.get(f"question_{q.id}", "")
                is_correct = selected == q.correct_option
                marks = q.marks if is_correct else 0
                Answer.objects.create(
                    result=result, question=q, selected_option=selected,
                    marks_awarded=marks, graded_by_staff=False,
                )
                obtained_marks += marks
            else:  # LONG answer — cannot auto-grade, staff grades later
                text = request.POST.get(f"question_{q.id}", "")
                Answer.objects.create(
                    result=result, question=q, text_answer=text,
                    marks_awarded=None, graded_by_staff=False,
                )
                all_graded = False

        result.obtained_marks = obtained_marks
        result.fully_graded = all_graded
        result.save()
        return redirect("result_detail", exam_id=exam.id)

    return render(request, "exams/take_exam.html", {"exam": exam, "questions": questions})


def _is_staff_or_admin(user):
    return user.is_authenticated and user.role in ("STAFF", "ADMIN")


@login_required
@user_passes_test(_is_staff_or_admin)
def grade_answers_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    ungraded = Answer.objects.filter(
        result__exam=exam, question__question_type="LONG", marks_awarded__isnull=True
    ).select_related("result", "question", "result__student")

    if request.method == "POST":
        for answer in ungraded:
            marks_str = request.POST.get(f"marks_{answer.id}")
            if marks_str:
                answer.marks_awarded = int(marks_str)
                answer.graded_by_staff = True
                answer.save()

        # Recalculate results whose answers were just graded
        result_ids = set(ungraded.values_list("result_id", flat=True))
        for result in Result.objects.filter(id__in=result_ids):
            all_answers = result.answers.all()
            result.obtained_marks = sum(a.marks_awarded or 0 for a in all_answers)
            result.fully_graded = all(a.marks_awarded is not None for a in all_answers)
            result.save()

        return redirect("grade_answers", exam_id=exam.id)

    return render(request, "exams/grade_answers.html", {"exam": exam, "ungraded": ungraded})

@login_required
@user_passes_test(_is_staff_or_admin)
def question_paper_view(request, exam_id):
    """
    Renders approved questions as a printable exam paper (MCQs in Part A,
    long-answer in Part B). Staff uses the browser's Print/Save-as-PDF to
    get a physical/PDF copy to hand out to students.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    mcqs = exam.questions.filter(question_type="MCQ")
    long_questions = exam.questions.filter(question_type="LONG")
    total_marks = sum(q.marks for q in exam.questions.all())
    return render(request, "exams/question_paper.html", {
        "exam": exam, "mcqs": mcqs, "long_questions": long_questions, "total_marks": total_marks,
    })