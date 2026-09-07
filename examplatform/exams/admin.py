from django.contrib import admin
from .models import Question, Exam, Result, Answer

admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(Answer)