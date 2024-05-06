from django.contrib import admin
from django.urls import include, path
from .settings import DEBUG


urlpatterns = [
    path('api/v1/admin_panel/admin/', admin.site.urls),
    path('api/', include('movies.api.urls')),
]

if DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
