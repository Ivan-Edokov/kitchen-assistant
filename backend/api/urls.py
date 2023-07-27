from django.urls import include, path
from rest_framework import routers

from .views import (
    UserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    SubscriptionViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
