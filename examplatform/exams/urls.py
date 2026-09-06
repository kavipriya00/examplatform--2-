from django.urls import path
from . import views

urlpatterns = [
    path("", views.exam_list_view, name="exam_list"),
    path("<int:exam_id>/take/", views.take_exam_view, name="take_exam"),
]
