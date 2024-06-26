from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient, Tag
from users.models import User
from .utils import add_subscribed

MESSAGES = {
    'username_invalid': 'Недопустимое имя',
    'current_password_invalid': 'Текущий пароль неверный.',
    'ingredients_unic': 'Невозможно добавить одинаковый ингредиент'
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
            'password': {'write_only': True},
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
        return add_subscribed(obj, request)


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

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализер для Тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализер для Рецептов"""

    author = UserSerializer(required=False)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients',
        many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

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
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):

        unic_ingredients = list()
        for ingredient in data['recipe_ingredients']:
            if ingredient in unic_ingredients:
                raise serializers.ValidationError(MESSAGES['ingredients_unic'])
            unic_ingredients.append(ingredient)
        return data

    def create_ingredients_tags(self, instance, ingredients, tags):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient_id=ingrow['ingredient']['id'],
                recipe=instance,
                amount=ingrow['amount']
            ) for ingrow in ingredients]
        )
        instance.tags.set(tags)

    def create(self, validated_data):

        validated_data['author'] = self.context['request'].user
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tag_list = self.initial_data['tags']
        instance = Recipe.objects.create(**validated_data)
        instance.tags.set(tag_list)
        self.create_ingredients_tags(instance, recipe_ingredients, tag_list)
        return instance

    def update(self, instance, validated_data):

        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tag_list = self.initial_data['tags']
        instance.recipe_ingredients.all().delete()
        self.create_ingredients_tags(instance, recipe_ingredients, tag_list)
        return super().update(instance, validated_data)

    def status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if (
                request.user.is_authenticated
                and obj.filter(id=request.user.id).exists()
            ):
                return True
        return False

    def get_is_favorited(self, obj):

        return self.status(obj.favorite)

    def get_is_in_shopping_cart(self, obj):

        return self.status(obj.shopping_card)


class RecipeShotSerializer(serializers.ModelSerializer):
    """Сериализер для Рецептов.
    Информация о рецепте для листа подписок и избранное.
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
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'recipes',
            'recipes_count',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):

        request = self.context.get('request')
        return add_subscribed(obj, request)

    def get_recipes_count(self, obj):
        return User.objects.get(id=obj.id).recipes.count()
