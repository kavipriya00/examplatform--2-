from django.urls import path
from . import views

urlpatterns = [
    path("<int:exam_id>/", views.result_detail_view, name="result_detail"),
    path("", views.my_results_view, name="my_results"),
    path("analytics/", views.analytics_view, name="analytics"),
]
