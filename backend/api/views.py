# import datetime
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User, Subscription
from ingredients.models import Ingredient
from recipes.models import Recipe, Tag
from .filters import RecipesFilter

from foodgram import settings
from .permissions import (
    RegisterProfileOrAutorised,
    OnlyGet,
    OnlyGetAutorised,
    GetOrGPPDAutorized,
)
from .serializers import (
    UserSerializer,
    UserSetPasswordSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    SubscriptionSerializer,
    RecipeShotSerializer,
)
from .utils import render_to_pdf

MESSAGES = {
    'self_subscription': 'Самостоятельная подписка не допускается.',
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
    permission_classes = (RegisterProfileOrAutorised,)
    lookup_field = 'id'

    def create(self, request):
        """Самостоятельная регистрация пользователя.
        Использует UserSignupSerializer.
        """

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение экземпляра пользователя self user."""

        serializer = UserSerializer(request.user, context={"request": request})
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

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, id=None):
        """Подпишитесь на пользователя, если метод POST.
        Отключена подписка на себя и дубль подписка.
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
    permission_classes = (OnlyGet,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ВьюСет для Рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (GetOrGPPDAutorized,)

    def create(self, request, *args, **kwargs):
        request.data['tag_list'] = request.data.pop('tags')
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data['tag_list'] = request.data.pop('tags')
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def add_remove_m2m_relation(
            self, request, model_main, model_mgr, pk, serializer_class
    ):
        """Добавьте отношение "многие ко многим" к пользовательской модели,
        если метод POST.
        Отключены двойные записи. Отключены двойные записи.
        Удалите рецепт из избранного, если метод УДАЛЕН.
        Удалите отношение "многие ко многим", если метод DELETE.
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

    @action(detail=False, methods=['get'])
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
        # timenow = datetime.datetime.now()
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
    permission_classes = (OnlyGet,)


class SubscriptionViewSet(viewsets.ModelViewSet):

    serializer_class = SubscriptionSerializer
    permission_classes = (OnlyGetAutorised,)

    def get_queryset(self):
        user = self.request.user
        followed_people = (
            Subscription.objects.filter(follower=user).values('follow')
        )
        subscription = User.objects.filter(id__in=followed_people)
        return subscription
