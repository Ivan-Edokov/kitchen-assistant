from django.db.models import OuterRef, Prefetch, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response

from foodgram import settings
from users.models import Subscription, User
from ingredients.models import Ingredient
from recipes.models import Recipe, Tag
from .filters import IngredientSearchFilter
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShotSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer,
                          UserSetPasswordSerializer)
from .utils import render_to_pdf

MESSAGES = {
    'self_subscription': 'Подписка на себя не допускается.',
    'double_subscription': 'Двойная подписка не допускается.',
    'no_subscribed': 'Ошибка отмены подписки, вы не были подписаны.',
    'relation_already_exists': 'Эта связь уже существует.',
    'relation_not_exists': 'Не удается удалить. Этой связи не существует.',
    'pdf_about': 'Приятного аппетита',
}


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet управления пользователями.
    Запросы к пользователю осуществляются по username.
    При обращении на 'me' пользователь получает/изменяет свою запись."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'id'

    def create(self, request):
        """Самостоятельная регистрация пользователя.
        Использует UserSignupSerializer.
        """

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=False, methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Получение экземпляра пользователя self user."""

        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False, methods=['post'],
        permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        """Самостоятельная смена пароля.
        Endpoint /set_password/.
        """

        serializer = UserSetPasswordSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Подпишитесь на пользователя, если метод POST.
        Отключена подписка на себя и дубль подписки.
        Отписаться, если метод DELETE.
        Отключена отмена подписки, если никто не подписан."""

        if int(id) == request.user.id:
            return Response(
                {"detail": MESSAGES["self_subscription"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_user = get_object_or_404(User, id=id)
        me = get_object_or_404(User, id=request.user.id)

        if request._request.method == "POST":
            if me.follower.filter(follow=follow_user).exists():
                return Response(
                    {"detail": MESSAGES["double_subscription"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            me.follower.create(follow=follow_user)
            serializer = SubscriptionSerializer(follow_user)
            return Response(serializer.data)

        if not me.follower.filter(follow=follow_user).exists():
            return Response(
                {"detail": MESSAGES["no_subscribed"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        me.follower.filter(follow=follow_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """Набор представлений для ингредиентов.
    Поддержка только GET, ограниченная permission.
    Поддержка поиска по имени пользователя"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ВьюСет для Рецептов"""

    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):

        queryset = Recipe.objects.all()
        tag_list = self.request.GET.getlist('tags')
        if tag_list:
            queryset = queryset.filter(tags__slug__in=tag_list).distinct()

        author = self.request.GET.get("author")
        if author:
            queryset = queryset.filter(author__id=author)

        if not self.request.user.is_authenticated:
            return queryset

        is_in_shopping_cart = self.request.GET.get("is_in_shopping_cart")
        if is_in_shopping_cart:
            queryset = queryset.filter(shopping_card=self.request.user)

        is_favorited = self.request.GET.get("is_favorited")
        if is_favorited:
            queryset = queryset.filter(favorite=self.request.user)

        return queryset

    def add_remove_m2m_relation(
            self, request, model_main, model_mgr, pk, serializer_class
    ):
        """Добавить отношение "многие ко многим" к пользовательской модели,
        если метод POST.
        Отключены двойные записи.
        Удалить рецепт из избранного, если метод УДАЛЕН.
        Удалить отношение "многие ко многим", если метод DELETE.
        Отключено удаление, если рецепта нет в избранном.
        Отключено удаление, если связь не существует."""

        main = get_object_or_404(model_main, pk=pk)
        manager = getattr(main, model_mgr)

        if request._request.method == 'POST':
            if manager.filter(id=request.user.id).exists():
                return Response(
                    {'detail': MESSAGES['relation_already_exists']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            manager.add(request.user)
            serializer = serializer_class(main)
            return Response(serializer.data)

        if not manager.filter(id=request.user.id).exists():
            return Response(
                {'detail': MESSAGES['relation_not_exists']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        manager.remove(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавить любимый рецепт, если метод POST.
        Отключены дубликаты записи.
        Удалить рецепт из избранного, если метод DELETE.
        Отключено удаление, если рецепта нет в избранном"""

        return self.add_remove_m2m_relation(
            request, Recipe, 'favorite', pk, RecipeShotSerializer
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавить в карточку покупок пользователя рецепт,
        если используется метод POST.
        Отключены дубликаты записи.
        Удалить рецепт из карточки покупок, если метод DELETE."""

        return self.add_remove_m2m_relation(
            request, Recipe, 'shopping_card', pk, RecipeShotSerializer
        )

    @action(
        detail=False, methods=['get'],
        permission_classes=(AuthorOrReadOnly,))
    def download_shopping_cart(self, request):

        card_ingredients = {}
        card_recipes = []
        user_recipes = Recipe.objects.filter(shopping_card=request.user)
        for recipe in user_recipes:
            card_recipes.append(recipe.name)
            recipe_ingredients = recipe.recipe_ingredients.all()
            for ingredient in recipe_ingredients:
                if ingredient.ingredient.id in card_ingredients:
                    amount = (
                        ingredient.amount
                        + card_ingredients[ingredient.ingredient.id]['amount']
                    )
                else:
                    amount = ingredient.amount
                card_ingredients[ingredient.ingredient.id] = {
                    'name': ingredient.ingredient.name,
                    'measurement_unit': ingredient.ingredient.measurement_unit,
                    'amount': amount,
                }
        timenow = timezone.now()
        time_label = timenow.strftime("%b %d %Y %H:%M:%S")
        template_card = 'download_shopping_cart.html'
        context = {
            'pagesize': settings.PDF_PAGE_SIZE,
            "card_recipes": card_recipes,
            "card_ingredients": card_ingredients,
            "time_label": time_label,
            "about": MESSAGES["pdf_about"],
        }
        return render_to_pdf(template_card, context)


class TagViewSet(viewsets.ModelViewSet):
    """ВьюСет для Тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (permissions.AllowAny,)
    pagination_class = None


class SubscriptionViewSet(viewsets.ModelViewSet):

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        followed_people = (
            Subscription.objects.filter(follower=user).values('follow')
        )
        subscription = User.objects.filter(id__in=followed_people)
        recipes_limit = int(self.request.GET.get("recipes_limit"))
        if recipes_limit:
            subqry = Subquery(
                Recipe.objects.filter(author=OuterRef("author")).values_list(
                    "id", flat=True
                )[:recipes_limit]
            )

            subscription = subscription.prefetch_related(
                Prefetch(
                    "recipes", queryset=Recipe.objects.filter(id__in=subqry)
                )
            )

        return subscription
