from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, Tag

from .permissions import RegisterProfileOrAutorised, OnlyGet
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    UserInstanceSerializer,
    UserSetPasswordSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet управления пользователями.
    Запросы к пользователю осуществляются по username.
    При обращении на 'me' пользователь получает/изменяет свою запись."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (RegisterProfileOrAutorised,)
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        """Самостоятельная регистрация пользователя.
        Использует UserSignupSerializer.
        """

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    def retrieve(self, request, username=None):
        """Получение экземпляра пользователя по имени пользователя.
        Запрос на /me/ возвращает самого пользователя
        """

        if username == 'me':
            username = request.user.username
        user = get_object_or_404(self.queryset, username=username)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Самостоятельная смена пароля.
        Endpoint /set_password/.
        """

        serializer = UserSetPasswordSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """Набор представлений для ингредиентов.
    Поддержка только GET, ограниченная permission.
    Поддержка поиска по имени пользователя"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (OnlyGet,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ВьюСет для Рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = ()


class TagViewSet(viewsets.ModelViewSet):
    """ВьюСет для Тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (OnlyGet,)
