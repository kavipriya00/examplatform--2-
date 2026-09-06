from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_syllabus_view, name="upload_syllabus"),
    path("<int:syllabus_id>/generate/", views.generate_questions_view, name="generate_questions"),
    path("<int:syllabus_id>/review/", views.review_questions_view, name="review_questions"),
    path("question/<int:question_id>/approve/", views.approve_question_view, name="approve_question"),
    path("question/<int:question_id>/reject/", views.reject_question_view, name="reject_question"),
]
