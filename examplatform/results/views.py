from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from exams.models import Result, Exam


@login_required
def result_detail_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    result = get_object_or_404(Result, student=request.user, exam=exam)
    return render(request, "results/result_detail.html", {"result": result, "exam": exam})


@login_required
def my_results_view(request):
    results = Result.objects.filter(student=request.user).select_related("exam")
    return render(request, "results/my_results.html", {"results": results})


@login_required
def analytics_view(request):
    # Simple aggregation: average score per exam (this is the "AI Learning
    # Analytics" module in plain-SQL form — swap in an LLM summary later).
    exam_stats = (
        Exam.objects.annotate(avg_score=Avg("results__score"))
        .values("title", "avg_score")
    )
    return render(request, "results/analytics.html", {"exam_stats": exam_stats})
