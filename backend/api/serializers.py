from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients, Tag
from users.models import User


MESSAGES = {
    'username_invalid': 'Недопустимое имя',
    'current_password_invalid': 'Текущий пароль неверный.',
}


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор самостоятельной регистрации пользователя.
    Имя 'me' исключено. Проверка пароля."""

    is_subscribed = serializers. SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if (
                request.user.is_authenticated
                and request.user.follower.filter(follow=obj).exists()
            ):
                return True
        return False


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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализер для Ингидиента"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализер для Тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализер для Рецептов"""

    author = UserSerializer()
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'ingredients',
            'tags',
        )


class RecipeShotSerializer(serializers.ModelSerializer):
    """Сериализер для Рецептов.
    Информация о рецепти для листа подписок
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализер для подписки."""

    recipes = RecipeShotSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'recipes',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return True
