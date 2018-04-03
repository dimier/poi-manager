from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import fields, serializers


__all__ = [
    'SelfProfileSerializer',
    'RegistrationSerializer',
    'AuthTokenSerializer',
]

User = get_user_model()


class SelfProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'has_usable_password']
        read_only_fields = ['id', 'username', 'email']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }


class RegistrationSerializer(serializers.ModelSerializer):
    password = fields.CharField(allow_blank=False, max_length=10000, validators=[validate_password])

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError(_('Пользователь с таким e-mail уже зарегистрирован'))

        return value

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }


class AuthTokenSerializer(serializers.Serializer):
    username = fields.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        # The authenticate call simply returns None for is_active=False
        # users. (Assuming the default ModelBackend authentication
        # backend.)
        if not user:
            msg = _('Не удается войти. Пожалуйста, проверьте правильность написания e-mail и пароля.')
            raise ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
