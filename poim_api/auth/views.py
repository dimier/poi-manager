import random
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework import generics, status
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from poim_api.utils import exceptions
from poim_api.utils.views import CustomPostMixin
from poim_api.auth.serializers import *


__all__ = [
    'RegistrationView',
    'LoginView',
    'LogoutView',
]

logger = logging.getLogger(__name__)

User = get_user_model()


class LoginUserMixin:
    def login_user(self, user):
        if self.request.user.is_authenticated and user == self.request.user and self.request.auth:
            auth_token = self.request.auth
        else:
            auth_token, created = AuthToken.objects.get_or_create(user=user)

        user_logged_in.send(sender=type(user), request=self.request, user=user)

        self.request.user = user
        self.request.auth = auth_token

        return auth_token

    def make_response_data(self, user, auth_token):
        serializer = SelfProfileSerializer(user, context=self.get_serializer_context())

        return {
            'profile': serializer.data,
            'auth_token': auth_token.key,
        }


class RegistrationView(LoginUserMixin, generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.create_user(serializer.validated_data)
        auth_token = self.login_user(user)

        response_data = self.make_response_data(user, auth_token)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def create_user(self, data):
        allowed_fields = ['username', 'first_name', 'last_name', 'password', 'email']
        kwargs = {k: v for k, v in data.items() if k in allowed_fields}
        kwargs['date_joined'] = now()
        kwargs['last_login'] = kwargs['date_joined']

        try:
            with transaction.atomic():
                user = User.objects.create_user(**kwargs)
        except IntegrityError as e:
            try:
                User.objects.get(email=kwargs['username'])
            except ObjectDoesNotExist:
                raise e  # ошибка не в добавлении пользователя с тем же username
            else:
                raise exceptions.Conflict()

        return user


class LoginView(LoginUserMixin, CustomPostMixin, generics.GenericAPIView):
    serializer_class = AuthTokenSerializer
    success_status = status.HTTP_200_OK

    def make_response(self, serializer):
        data = self.make_response_data(self.request.user, self.request.auth)
        return Response(data, status=self.success_status)

    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        self.login_user(user)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        self.request.auth.delete()
        user_logged_out.send(sender=type(self.request.user), request=self.request, user=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
