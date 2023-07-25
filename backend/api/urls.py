from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
