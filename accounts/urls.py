from django.urls import path
from .views import (
    signup,
    login,
    search_email,
    set_new_password
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('signup/', signup),
    path('login/', login),
    path('search_email/', search_email),
    path('set_new_password/', set_new_password),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)