from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('', include('poim_api.auth.urls')),
    path('', include('poim_api.points.urls')),
    path('docs/', include_docs_urls(title='POI Manager API')),
]
