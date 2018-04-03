from django.contrib import admin
from django.urls import path, include
from poim_api.points.views import *


urlpatterns = [
    path('points', PointListView.as_view()),
    path('points/<int:pk>', PointDetailView.as_view()),
    path('points/<int:pk>/deleted', PointUndeleteView.as_view()),
]
