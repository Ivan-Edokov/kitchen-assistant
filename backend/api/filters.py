from django_filters import rest_framework
from recipes.models import Recipe


class RecipesFilter(rest_framework.FilterSet):
    """Фильтр для вьюсета TitleViewSet"""

    tags = rest_framework.CharFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )

    class Meta:
        model = Recipe
        fields = ['tags']
