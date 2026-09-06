from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.dashboard_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('results/', include('results.urls')),
    path('syllabus/', include('syllabus_ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
