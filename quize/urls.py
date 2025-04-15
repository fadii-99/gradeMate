from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('upload_quiz/', views.upload_quiz),
    path('dashboard-stats/', views.dashboard),
    path('quiz_view/', views.quiz_view),
    path('get_all_quizes/', views.get_all_quizes),
    path('check_plagiarism/', views.check_plagiarism),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)