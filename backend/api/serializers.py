from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from users.models import User


MESSAGES = {
    'username_invalid': 'Недопустимое имя',
    'current_password_invalid': 'Текущий пароль неверный.',
}


class UserSerializer(serializers.ModelSerializer):
    """Serialiser пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )
        lookup_field = 'username'


class UserInstanceSerializer(serializers.ModelSerializer):
    """User Instance Serializer."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )
        lookup_field = 'username'


class UserSignupSerializer(serializers.ModelSerializer):
    """Сериализатор самостоятельной регистрации пользователя.
    Имя 'me' исключено. Проверка пароля."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(MESSAGES['username_invalid'])
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return make_password(value)


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для самостоятельной смены пароля.
    Произведена проверка основного пароля.
    """

    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('password', 'new_password', 'current_password')
        extra_kwargs = {
            'password': {'write_only': True},
        }
        lookup_field = 'username'

    def validate(self, data):
        """Проверка паролей."""

        if not check_password(
            data['current_password'], self.instance.password
        ):
            raise serializers.ValidationError(
                {'current_password': MESSAGES['current_password_invalid']}
            )

        try:
            validate_password(data['new_password'])
        except ValidationError as exc:
            raise serializers.ValidationError({'new_password': str(exc)})

        data['password'] = make_password(data['new_password'])
        return data
