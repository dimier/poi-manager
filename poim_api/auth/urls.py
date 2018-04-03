from django.contrib import admin
from django.urls import path, include
from poim_api.auth.views import *


urlpatterns = [
    path('register', RegistrationView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
]
