from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("escola/", include("escola.urls")),  # <- rota para aplicação web escola
    path("portfolio/", include("portfolio.urls")),
]

# Serve ficheiros media em DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
